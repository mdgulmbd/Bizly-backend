from fastapi import FastAPI
from pydantic import BaseModel
import os
import requests

app = FastAPI(title="Bizly Backend")


class ChatRequest(BaseModel):
    messages: list
    fast: bool = False


@app.get("/")
def home():
    return {"status": "Bizly backend is running"}


@app.post("/chat")
def chat(request: ChatRequest):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {"error": "GEMINI_API_KEY is not configured"}

    # Gemini API
    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-2.5-flash:generateContent"
    )

    # Convert Bizly messages to Gemini format
    contents = []

    for message in request.messages:
        role = message.get("role", "user")
        text = message.get("content", "")

        if role == "assistant":
            gemini_role = "model"
        else:
            gemini_role = "user"

        contents.append({
            "role": gemini_role,
            "parts": [{"text": text}]
        })

    response = requests.post(
        url,
        params={"key": api_key},
        json={"contents": contents},
        timeout=60
    )

    if response.status_code != 200:
        return {
            "error": "Gemini API error",
            "details": response.text
        }

    data = response.json()

    try:
        answer = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return {"error": "No response received from Gemini"}

    return {"response": answer}
