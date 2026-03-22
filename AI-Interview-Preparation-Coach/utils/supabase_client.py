import os
from supabase import create_client, Client

def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise Exception("Supabase credentials not found in environment variables.")
        
    supabase: Client = create_client(url, key)
    return supabase
