import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Configuração com tratamento de erros
try:
    SUPABASE_URL = os.environ["SUPABASE_URL"]
    SUPABASE_KEY = os.environ["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except KeyError as e:
    raise RuntimeError(f"Variável de ambiente faltando: {str(e)}")
except Exception as e:
    raise RuntimeError(f"Erro ao conectar ao Supabase: {str(e)}")
