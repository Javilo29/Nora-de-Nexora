# -*- coding: utf-8 -*-
# Nora Diagnostic Test v7.5.2 - Saneamiento de Conectividad
import sys
import os
import time
from pathlib import Path

# Configurar entorno de Nora
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "Guiones"))

import ia_brain
from ia_paths import ASSETS_DIR, VISION_HISTORY_LOG

def run_diagnostic():
    print("🧠 [Nora Diagnostic]: Iniciando verificación de Saneamiento v7.5.2...")
    
    # Generar una imagen pesada para probar optimización
    heavy_img = ASSETS_DIR / "heavy_test.jpg"
    if not heavy_img.exists():
        print("🛠️ Generando imagen de prueba (>2MB) para verificar optimización...")
        try:
            from PIL import Image, ImageDraw
            # Imagen grande para superar los 2MB (ej: 4000x3000)
            img = Image.new('RGB', (4000, 3000), color=(240, 240, 240))
            d = ImageDraw.Draw(img)
            # Dibujar muchos patrones para que el JPG no compima tanto de golpe
            for i in range(0, 4000, 100):
                d.line([(i, 0), (i, 3000)], fill=(0,0,0), width=2)
            d.text((500,500), "TEST SANEAMIENTO v7.5.2", fill=(255,0,0))
            img.save(heavy_img, "JPEG", quality=95)
            print(f"✅ Imagen generada: {heavy_img.name} ({os.path.getsize(heavy_img)/1024/1024:.2f} MB)")
        except Exception as e:
            print(f"⚠️ No se pudo generar imagen pesada: {e}")
            heavy_img = ASSETS_DIR / "test_invoice.png"

    print(f"👁️ Nora analizando archivo: {heavy_img.name}")
    
    admin_id = "1645060982"
    start_time = time.time()
    response = ia_brain.proceso_visión_datos(str(heavy_img), user_id=admin_id)
    duration = time.time() - start_time
    
    print("-" * 50)
    print(f"RESULTADO COGNITIVO:\n{response}")
    print("-" * 50)
    print(f"⏱️ Tiempo total de procesamiento: {duration:.2f} segundos")
    
    if "interrupción técnica" in response.lower():
        print("🚩 FALLO: El motor de visión tuvo una interrupción técnica.")
    else:
        print("✅ ÉXITO: El Saneamiento v7.5.2 es operativo.")
        
    with open(VISION_HISTORY_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] DIAGNOSTIC v7.5.2: {response[:100]}...\n")

if __name__ == "__main__":
    run_diagnostic()
