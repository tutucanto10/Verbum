import os 
from dotenv import load_dotenv

load_dotenv() #Para carregar as variaveis do .env na raiz

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_KEY")