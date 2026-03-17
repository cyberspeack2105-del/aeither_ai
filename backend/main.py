from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -----------------------------
# Config & Setup
# -----------------------------
# OpenRouter Config
API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = os.getenv("MODEL", "google/gemma-3-4b-it:free")

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(title="Aether AI - AI Server")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Request Schema
# -----------------------------
class Question(BaseModel):
    prompt: str
    language: str = "Tamil"  # Default language

# -----------------------------
# SYSTEM PROMPT CONFIGURATION
# -----------------------------
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
- (Add more if necessary for completeness)

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
# AI Function
# -----------------------------
def ask_deepseek(user_prompt: str, language: str):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": f"{get_system_prompt(language)}\n\nUser Question: {user_prompt}"}
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=20)
        
        if response.status_code != 200:
            return f"❌ AI server error: {response.text}"
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

# -----------------------------
# API Endpoint
# -----------------------------
@app.post("/ask")
def ask_ai(question: Question):
    answer = ask_deepseek(question.prompt, question.language)
    return {"answer": answer}

# Root check
@app.get("/")
def read_root():
    return {"message": "AI Server Running on Port 8000"}
