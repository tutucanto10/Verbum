# backend/app/services/analysis_service.py

import re
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv
import os
from pathlib import Path

# garante que vamos ler o .env da pasta backend
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client | None = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("⚠️ Supabase não configurado. Verifique SUPABASE_URL e SUPABASE_KEY no .env")

def analyze_progress(user_id: str, message: str, language: str):
    # análise simples
    errors = len(re.findall(r"\b(?:dont|wanna|aint)\b", message.lower()))
    score = max(0, 100 - errors * 5)

    # só tenta salvar se o supabase existir
    if supabase:
        supabase.table("user_progress").insert({
            "user_id": user_id,
            "message": message,
            "language": language,
            "score": score,
            "timestamp": datetime.utcnow().isoformat()
        }).execute()
    else:
        print("⚠️ Não foi possível salvar no Supabase (sem config).")

    return {"score": score, "feedback": f"Your message scored {score}/100!"}
