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
        return {
            "error": "GEMINI_API_KEY is not configured in Render Environment."
        }

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-2.5-flash:generateContent"
    )

    contents = []

    for message in request.messages:
        role = message.get("role", "user")
        text = message.get("content", "")

        if not text:
            continue

        if role == "assistant":
            gemini_role = "model"
        else:
            gemini_role = "user"

        contents.append({
            "role": gemini_role,
            "parts": [
                {"text": text}
            ]
        })

    if not contents:
        return {"error": "No message was received."}

    response = requests.post(
        url,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        },
        json={
            "contents": contents
        },
        timeout=60
    )

    if response.status_code != 200:
        return {
            "error": f"Gemini API error ({response.status_code})",
            "details": response.text
        }

    try:
        data = response.json()
        answer = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return {
            "error": "Gemini returned an unexpected response.",
            "details": response.text
        }

    return {"response": answer}
    
