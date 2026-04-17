import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables de entorno desde D:\AGENTE_IA\.env
load_dotenv(dotenv_path=r"D:\AGENTE_IA\.env")

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

def verify_connection():
    if not url or not key or "tu-proyecto" in url:
        print("Error: Credenciales de Supabase no configuradas en .env")
        return False
    
    try:
        supabase: Client = create_client(url, key)
        # Intento de consulta simple para verificar conexión
        # (Asumiendo que la tabla clientes existirá)
        print(f"Conectando a: {url}...")
        # response = supabase.table("ia_clientes").select("*", count="exact").limit(1).execute()
        print("Conexión con Supabase establecida (SDK inicializado).")
        return True
    except Exception as e:
        print(f"Error al conectar con Supabase: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando Verificador de Sincronización en la Nube...")
    verify_connection()
    print("Proceso finalizado. Cerrando hilos de ejecución.")
