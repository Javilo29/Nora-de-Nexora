# Proyecto: Nora de Nexora - Prueba de Conciencia Directa
# Este script prueba la conexión a Gemini sin pasar por Telegram
import os
import sys
from dotenv import load_dotenv

from ia_paths import ENV_FILE

load_dotenv(dotenv_path=str(ENV_FILE))

import google.generativeai as genai

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("ERROR: No se encontró GEMINI_API_KEY en .env")
    sys.exit(1)

print(f"[OK] API Key cargada: {API_KEY[:8]}...{API_KEY[-4:]}")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

print("[INFO] Enviando saludo a Gemini (timeout 30s)...")

try:
    response = model.generate_content(
        "Decí 'Hola Jefe, soy Nora de Nexora' en español rioplatense, en una sola línea.",
        request_options={'timeout': 30}
    )
    print(f"[RESPUESTA GEMINI]: {response.text}")
    print("[OK] Cerebro de Nora FUNCIONAL")
except Exception as e:
    print(f"[ERROR {type(e).__name__}]: {e}")
    import traceback
    traceback.print_exc()
