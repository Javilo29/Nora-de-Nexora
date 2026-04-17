# -*- coding: utf-8 -*-
# Nora Vision Local v7.5 - Módulo de Captura Independiente
import cv2
import time
import os
import sys
from pathlib import Path

# Ajustar path para encontrar los guiones
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "Guiones"))

import ia_brain
from ia_paths import VISION_HISTORY_DIR, VISION_HISTORY_LOG

def capture_and_analyze():
    """Captura un frame de la webcam y lo envía al cerebro multimodal. v8.0 Cloud Ready."""
    print("📸 Nora Vision: Iniciando captura de frame...")
    
    try:
        # Usar OpenCV para capturar (sin ventana)
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise Exception("Webcam no detectada o deshabilitada.")
        
        # Dar tiempo a la cámara para ajustar el brillo
        time.sleep(1)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise Exception("No se pudo leer el frame de la cámara.")
            
        # Guardar en Historial Visual (Disco D)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        file_name = f"capture_{timestamp}.jpg"
        file_path = VISION_HISTORY_DIR / file_name
        cv2.imwrite(str(file_path), frame)
        print(f"✅ Frame guardado en: {file_path}")
        
    except Exception as e:
        print(f"☁️ [MODO NUBE/AUDITORÍA]: Fallo de hardware detectado: {e}")
        print("📂 Nora activando 'Modo Auditoría Documental'. Escaneando Inbox...")
        # Lógica de fallback: usar el último archivo en Inbox o esperar mensaje
        from ia_paths import INBOX_DIR
        archivos = sorted(INBOX_DIR.glob("*"), key=os.path.getmtime, reverse=True)
        if archivos:
            file_path = archivos[0]
            print(f"📄 Procesando documento más reciente en Inbox: {file_path.name}")
        else:
            print("⏳ No hay documentos pendientes para auditoría.")
            return
    
    # Análisis Multimodal (Simulando usuario Javier si es proactivo)
    # Por ahora lo enviamos para reporte general
    response = ia_brain.analyze_multimodal_vision(str(file_path), user_id="1645060982")
    print(f"🧠 Nora respondió: {response}")
    
    # Registrar en log
    with open(VISION_HISTORY_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Captura Local: {response[:100]}...\n")

if __name__ == "__main__":
    print("👀 Nora Vision Local v7.5 activado (Modo Headless).")
    # Este script puede ser llamado por cron o un bucle simple
    # Por ahora, capturemos un frame de prueba
    capture_and_analyze()
