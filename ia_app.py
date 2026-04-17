# Nora Nexora v7.5.5 SRE - Main Server
import os
import threading
import sys
import gc
import psutil
import subprocess
import platform
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None
    print("Aviso: pyttsx3 no disponible. Modo voz desactivado.")

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
scripts_path = os.path.join(BASE_DIR, 'Guiones')
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, render_template_string, request, jsonify
import ia_telegram_bot
import ia_local_store
import ia_brain
from ia_whatsapp import nora_wa

# --- LIMPIEZA DE PUERTO ---
def kill_port(port):
    try:
        output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
        for line in output.splitlines():
            if "LISTENING" in line:
                pid = line.strip().split()[-1]
                print(f"🗑️ Liberando puerto {port} (PID: {pid})...")
                os.kill(int(pid), 9)
    except Exception: pass

# --- MOTOR DE VOZ v8.0 UNIVERSAL ---
def hablar_nora(texto):
    current_os = platform.system()
    print(f"🎙️ Nora Vocalizando ({current_os}): {texto}")
    
    if current_os == "Windows" and pyttsx3:
        try:
            # Inicialización perezosa para evitar bloqueos
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 1.0)
            engine.say(texto)
            engine.runAndWait()
        except Exception as e:
            print(f"⚠️ Error en locución local (Windows): {e}")
    elif current_os == "Windows" and not pyttsx3:
        print("⚠️ Modo voz local (Windows) desactivado por falta de pyttsx3.")
    else:
        # Modo Nube (Replit/Linux): Derivar a Telegram Admin
        print("☁️ Modo Nube detectado. Derivando voz a canal de texto/audio prioritario.")
        try:
            # Intentar usar el callback de telegram si está disponible
            if hasattr(ia_telegram_bot, 'send_voice_note'):
                 ia_telegram_bot.send_voice_note(texto)
            else:
                 ia_telegram_bot.hablar_callback_cloud(f"📢 [VOZ NORA]: {texto}")
        except Exception as e:
            print(f"⚠️ Error en derivación de voz cloud: {e}")

# --- SERVIDOR KEEPALIVE v7.5.5 ---
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Nora v7.5.5 | Groq SRE</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #f8fafc; padding: 2rem; }
        .card { background: #1e293b; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #f59e0b; margin-bottom: 1rem; }
        .status { color: #4ade80; font-weight: bold; }
        h1 { color: #f59e0b; }
    </style>
</head>
<body>
    <h1>🧠 Nora Nexora v8.2: Infraestructura Multinodal</h1>
    <div class="card">
        <div class="metric">Gateway: <span class="status">WhatsApp & Telegram Activos</span></div>
        <div class="metric">Watchdog: <span class="status">Protección de RAM Activada (12h)</span></div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    try:
        ram = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        return render_template_string(HTML_TEMPLATE, ram_usage=round(ram, 2))
    except: return "Nora Server Status: ERROR"

@app.route('/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode and token:
            if nora_wa.handle_webhook_verification(token):
                return challenge, 200
        return "Forbidden", 403
    else:
        # POST para mensajes entrantes
        data = request.get_json()
        nora_wa.process_incoming_message(data)
        return jsonify({"status": "ok"}), 200

def maintenance_watchdog():
    """Watchdog v8.2: Limpieza de logs y RAM cada 12 horas."""
    import time
    from ia_paths import LOGS_DIR, TMP_DIR
    
    while True:
        try:
            print("🛡️ Watchdog: Iniciando saneamiento de ciclos v8.2...")
            # Limpiar TMP
            for f in TMP_DIR.glob("*"):
                if f.is_file(): f.unlink()
            
            # Monitoreo de RAM
            ram_percent = psutil.virtual_memory().percent
            if ram_percent > 75:
                print(f"⚠️ Alerta RAM: {ram_percent}%. Forzando limpieza de basura...")
                gc.collect()
            
            print("✅ Watchdog: Saneamiento completado. Próximo ciclo en 12h.")
            time.sleep(12 * 3600) # 12 Horas
        except Exception as e:
            print(f"⚠️ Error en Watchdog: {e}")
            time.sleep(3600)

def run_flask(): app.run(host='0.0.0.0', port=8080)

# --- INICIO v7.5.5 ---
if __name__ == "__main__":
    print("🚀 Nora de Nexora v7.5.5 SRE: Lanzando Parche de Saneamiento...")
    kill_port(8080)
    kill_port(8888)
    
    gc.collect()
    
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    ia_telegram_bot.hablar_callback = hablar_nora
    hablar_nora("Sistema Multinodal v8.2 activo, Javier. WhatsApp y Telegram sincronizados en el Disco D")
    
    # Iniciar Watchdog v8.2 (RAM & Cleanup)
    wt = threading.Thread(target=maintenance_watchdog)
    wt.daemon = True
    wt.start()
    
    try:
        ia_telegram_bot.run_bot()
    except Exception as e:
        print(f"❌ Error crítico en el bot: {e}")