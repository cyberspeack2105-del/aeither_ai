from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
import motor.motor_asyncio
from passlib.context import CryptContext
import os
import shutil
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -----------------------------
# Config & Setup
# -----------------------------
# MongoDB Config
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = "chatbot"

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(title="Aether AI - Data Server")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files (for uploaded images)
# We assume 'static' folder is in the same directory as this file (backend/static)
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

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

# -----------------------------
# Models
# -----------------------------
class LoginRequest(BaseModel):
    name: str
    password: str

class ChatMessage(BaseModel):
    user_name: str
    chat_id: str
    message: str
    sender: str  # "user" or "bot"

# -----------------------------
# Auth Endpoints
# -----------------------------
@app.post("/register")
async def register(
    name: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    image: UploadFile = File(...)
):
    # Check if user exists
    existing_user = await users_collection.find_one({"name": name})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    existing_email = await users_collection.find_one({"email": email})
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Save Image
    file_location = f"static/uploads/{image.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    # Hash Password
    hashed_password = get_password_hash(password)

    # Store User
    # We store the FULL URL so frontend can just use it
    # Assumes server is running on localhost:8080
    image_full_url = f"http://127.0.0.1:8080/{file_location}"

    user_data = {
        "name": name,
        "email": email,
        "password": hashed_password,
        "image_url": image_full_url
    }
    await users_collection.insert_one(user_data)

    return {"message": "Registration successful", "user": name}

@app.post("/login")
async def login(login_data: LoginRequest):
    user = await users_collection.find_one({"name": login_data.name})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    if not verify_password(login_data.password, user["password"]):
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
        {"$sort": {"_id": -1}}, # Sort by newest first within the group? No, group first.
        {"$group": {
            "_id": "$chat_id",
            "last_message": {"$first": "$message"},
            "timestamp": {"$first": "$_id"}
        }},
        {"$sort": {"timestamp": -1}}
    ]
    cursor = db["chats"].aggregate(pipeline)
    history = await cursor.to_list(length=100)
    # Convert ObjectId to string
    for item in history:
        item["timestamp"] = str(item["timestamp"])
    return history

@app.get("/chat/{chat_id}")
async def get_chat(chat_id: str):
    cursor = db["chats"].find({"chat_id": chat_id}).sort("_id", 1)
    messages = await cursor.to_list(length=100)
    for msg in messages:
        msg["_id"] = str(msg["_id"])
    return messages

# Root check
@app.get("/")
def read_root():
    return {"message": "Data Server Running on Port 8080"}
