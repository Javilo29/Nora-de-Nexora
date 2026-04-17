# Proyecto: Nora de Nexora - MyJNexoraVisual
import urllib.request
import urllib.parse
from pathlib import Path

# Carga manual mínima
env_path = Path("D:/AGENTE_IA/.env")
conf = {}
if env_path.exists():
    with open(env_path, "r") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                conf[k] = v.strip("'").strip('"')

TOKEN = conf.get("TELEGRAM_TOKEN")
ADMIN_ID = conf.get("TELEGRAM_ADMIN_ID")

def send_test():
    if not TOKEN or not ADMIN_ID:
        print("❌ Faltan datos en .env")
        return
    
    msg = "🚀 Nora de Nexora: Test del Corazón OK. RAM Purificada."
    # URL directa codificada
    encoded_msg = urllib.parse.quote(msg)
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={ADMIN_ID}&text={encoded_msg}"
    
    print(f"DEBUG: Enviando a {ADMIN_ID}...")
    try:
        with urllib.request.urlopen(url) as response:
            print(f"📊 Status: {response.getcode()}")
            if response.getcode() == 200:
                print("✅ PULSO DETECTADO.")
    except Exception as e:
        print(f"❌ Fallo: {e}")

if __name__ == "__main__":
    send_test()
