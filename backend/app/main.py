from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.openai_service import chat_with_ai
from .models.chat_models import ChatRequest


app = FastAPI()

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = await chat_with_ai(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
