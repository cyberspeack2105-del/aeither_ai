from fastapi import FastAPI, HTTPException, Form, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
import motor.motor_asyncio
from passlib.context import CryptContext
import requests
import os
import shutil
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -----------------------------
# Config & Setup
# -----------------------------
API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = os.getenv("MODEL", "google/gemma-3-4b-it:free")

# MongoDB Config
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = "chatbot"

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(title="Aether AI Platform")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files Setup
# Ensure paths are correct for both local and Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOADS_DIR = os.path.join(STATIC_DIR, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Database Connection
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
users_collection = db["users"]

# -----------------------------
# Helpers
# -----------------------------
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_system_prompt(language: str):
    return f"""
- Be expansive: Don't just give one-sentence answers. Provide deep context.
- Accuracy: Ensure all facts, formulas, and theories are correct.
- Clarity: Use simple yet professional language.

ANSWER FORMAT (STRICT – YOU MUST FOLLOW THIS STRUCTURE FOR EVERY RESPONSE):

Title: 
# <Compelling and clear Topic Name>

Definition:
> <Provide a comprehensive, in-depth definition. Explain the core concept thoroughly in 3-5 sentences.>

Key Points:
- **Major Concept 1**: Detailed explanation of this point.
- **Major Concept 2**: Detailed explanation of this point.
- **Major Concept 3**: Detailed explanation of this point.
- **Major Concept 4**: Detailed explanation of this point.

Working / Detailed Explanation:
<Provide a step-by-step, logical breakdown of how the concept works. Use numbered lists or clear paragraphs. Include formulas if applicable.>

Applications:
- **Application 1**: Detailed description of how this is used in industry or research.
- **Application 2**: Detailed description of how this is used in daily life or technology.
- **Application 3**: Another significant application area.

Real-World Examples:
- **Example 1**: A specific, relatable scenario illustrating the concept.
- **Example 2**: Another concrete example or case study.

Final Insight / Conclusion:
<A thought-provoking summary that ties everything together and highlights the importance of the topic.>

Do NOT deviate from this structure. If the user asks a simple greeting or non-academic question, you may respond naturally but still aim for a premium, helpful tone.
"""

# -----------------------------
# Models
# -----------------------------
class Question(BaseModel):
    prompt: str
    language: str = "Tamil"

class LoginRequest(BaseModel):
    name: str
    password: str

class ChatMessage(BaseModel):
    user_name: str
    chat_id: str
    message: str
    sender: str

# -----------------------------
# AI Endpoint
# -----------------------------
@app.post("/ask")
def ask_ai(question: Question):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": f"{get_system_prompt(question.language)}\n\nUser Question: {question.prompt}"}],
        "temperature": 0.2
    }
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=20)
        if response.status_code != 200: return {"answer": f"❌ AI server error: {response.text}"}
        data = response.json()
        return {"answer": data["choices"][0]["message"]["content"]}
    except Exception as e:
        return {"answer": f"❌ Connection Error: {str(e)}"}

# -----------------------------
# Auth Endpoints
# -----------------------------
@app.post("/register")
async def register(
    request: Request,
    name: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    image: UploadFile = File(...)
):
    if await users_collection.find_one({"name": name}):
        raise HTTPException(status_code=400, detail="Username already taken")
    if await users_collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate filename and save locally
    filename = f"{name}_{image.filename}"
    file_path = os.path.join(UPLOADS_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    # Store dynamic URL
    base_url = str(request.base_url).rstrip("/")
    image_url = f"{base_url}/static/uploads/{filename}"

    user_data = {
        "name": name,
        "email": email,
        "password": get_password_hash(password),
        "image_url": image_url
    }
    await users_collection.insert_one(user_data)
    return {"message": "Registration successful", "user": name}

@app.post("/login")
async def login(login_data: LoginRequest):
    user = await users_collection.find_one({"name": login_data.name})
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    return {"message": "Login successful", "user": user["name"], "image_url": user["image_url"]}

# -----------------------------
# Chat Endpoints
# -----------------------------
@app.post("/save_chat")
async def save_chat(chat_data: ChatMessage):
    await db["chats"].insert_one(chat_data.dict())
    return {"message": "Chat saved"}

@app.get("/history/{user_name}")
async def get_history(user_name: str):
    pipeline = [
        {"$match": {"user_name": user_name}},
        {"$group": {"_id": "$chat_id", "last_message": {"$first": "$message"}, "timestamp": {"$first": "$_id"}}},
        {"$sort": {"timestamp": -1}}
    ]
    cursor = db["chats"].aggregate(pipeline)
    history = await cursor.to_list(length=100)
    for item in history: item["timestamp"] = str(item["timestamp"])
    return history

@app.get("/chat/{chat_id}")
async def get_chat(chat_id: str):
    cursor = db["chats"].find({"chat_id": chat_id}).sort("_id", 1)
    messages = await cursor.to_list(length=100)
    for msg in messages: msg["_id"] = str(msg["_id"])
    return messages

@app.get("/")
def read_root(): return {"message": "Aether AI Unified Server Running"}
