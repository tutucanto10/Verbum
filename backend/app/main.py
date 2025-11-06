from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.openai_service import chat_with_ai

app = FastAPI()

import logging
logging.basicConfig(level=logging.DEBUG)


class ChatRequest(BaseModel):
    user_id: str
    message: str
    language: str  # "en" or "es"
    history: list = []  # optional: [{role: "user"/"assistant", content: "..."}]

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = await chat_with_ai(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
