# Proyecto: Nora de Nexora - MyJNexoraVisual
import requests
import os
from dotenv import load_dotenv
from ia_paths import ENV_FILE

load_dotenv(dotenv_path=str(ENV_FILE))

TOKEN = os.environ.get("TELEGRAM_TOKEN")
ADMIN_ID = os.environ.get("TELEGRAM_ADMIN_ID")

def send_emergency_ping():
    if not TOKEN or not ADMIN_ID:
        print("❌ Error: Credenciales no encontradas.")
        return False
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_ID,
        "text": "🚀 Nora de Nexora: ¡He sobrevivido a la purga de RAM! Sistema en línea y optimizado, Jefe."
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✅ Ping de emergencia enviado con éxito.")
            return True
        else:
            print(f"❌ Error al enviar ping: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Excepción en red: {e}")
        return False

if __name__ == "__main__":
    send_emergency_ping()
