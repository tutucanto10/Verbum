from supabase import create_client, Client
from app.core.config import SUPABASE_URL, SUPABASE_ANON_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)