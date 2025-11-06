# >>> INÍCIO PATCH: openai_service.py
from openai import AsyncOpenAI
from app.services.analysis_service import analyze_progress
from dotenv import load_dotenv
import os
from pathlib import Path

# Carregar .env da pasta backend
BASE_DIR = Path(__file__).resolve().parents[2]  # sobe dois níveis (app/services → backend)
env_path = BASE_DIR / ".env"
print(f"🟣 Carregando .env de: {env_path}")
load_dotenv(dotenv_path=env_path)

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
print("🔑 OPENAI_API_KEY:", OPENAI_KEY)

# Instanciar o cliente de forma segura (sem proxies)
client = AsyncOpenAI(api_key=OPENAI_KEY)

# Mensagem base do sistema
SYSTEM_PROMPT = """
You are a language learning assistant.
Your goals:
1. Respond naturally in the target language (English or Spanish).
2. Be friendly and encourage learning.
3. Correct mistakes politely when appropriate.
4. Optionally explain the correction if the user seems to be practicing.
"""

async def chat_with_ai(request):
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(request.history)
        messages.append({"role": "user", "content": request.message})

        # Chamada correta para o novo SDK OpenAI (Async)
        completion = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.8,
        )

        ai_message = completion.choices[0].message.content

        # Chamada de análise personalizada
        analysis = analyze_progress(request.user_id, request.message, request.language)

        return {
            "reply": ai_message,
            "analysis": analysis
        }

    except Exception as e:
        print("❌ Erro no chat_with_ai:", str(e))
        return {
            "reply": "Ocorreu um erro ao processar sua mensagem.",
            "error": str(e)
        }
# >>> FIM PATCH
