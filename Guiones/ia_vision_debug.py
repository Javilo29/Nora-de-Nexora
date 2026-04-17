# -*- coding: utf-8 -*-
# Nora Autopsy v11.1 (Render Cloud) - Vision Diagnostics
import sys
import os
import time
import traceback
from pathlib import Path

# Configurar entorno de Nora
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "Guiones"))

import ia_brain
from ia_paths import VISION_HISTORY_DIR, VISION_HISTORY_LOG

def run_autopsy():
    print("🧠 [Nora Autopsy v11.1 (Render Cloud)]: Iniciando diagnóstico de bajo nivel...")
    
    # Localizar la última imagen de vision_history
    last_img = VISION_HISTORY_DIR / "img_AQADTAxrG1Eg0EZ-.jpg"
    if not last_img.exists():
        # Buscar cualquiera en el directorio
        files = sorted(VISION_HISTORY_DIR.glob("*.jpg"), key=os.path.getmtime)
        if files:
            last_img = files[-1]
        else:
            print("❌ No se encontraron imágenes en vision_history para la autopsia.")
            return

    print(f"👁️ Analizando evidencia: {last_img.resolve()}")
    
    admin_id = "1645060982"
    
    # Forzar carga de .env para asegurar que GEMINI_API_KEY esté presente
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)
    
    key = os.getenv("GEMINI_API_KEY")
    print(f"🔑 Verificando API Key (Gemini): {'PRESENTE (Len:' + str(len(key)) + ')' if key else 'FALTANTE'}")
    
    # Ejecutar proceso_visión_datos
    try:
        print("-" * 50)
        print("🚀 Lanzando petición a los motores de visión...")
        response = ia_brain.proceso_visión_datos(str(last_img), user_id=admin_id)
        print("-" * 50)
        print(f"RESULTADO FINAL:\n{response}")
        print("-" * 50)
        
        if "interrupción técnica" in response.lower():
            print("🚩 DIAGNÓSTICO: Fallo detectado. Revise el traceback arriba.")
        else:
            print("✅ DIAGNÓSTICO: El motor respondió correctamente en modo manual.")
            
    except Exception:
        print("❌ FALLO CATASTRÓFICO DURANTE LA AUTOPSIA:")
        traceback.print_exc()

if __name__ == "__main__":
    run_autopsy()
