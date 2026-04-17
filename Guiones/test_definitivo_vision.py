# -*- coding: utf-8 -*-
# Nora Vision Test Definitivo v8.0 - VALIDACIÓN GROQ HIGH-RES
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

def run_test_definitivo():
    print("🧠 [Nora v8.0]: Iniciando Prueba Definitiva de Visión (Groq High-Res)...")
    
    # Generar una imagen 4K para validar la rapidez de redimensionamiento y procesamiento de Groq
    high_res_img = ASSETS_DIR / "high_res_audit.jpg"
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        print("🛠️ Generando entorno simulado 4K (3840x2160)...")
        img = Image.new('RGB', (3840, 2160), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        
        # Simular una factura compleja
        d.rectangle([50, 50, 3790, 2110], outline=(0,0,0), width=5)
        d.text((100, 100), "FACTURA DE AUDITORIA SRE v8.0", fill=(0,0,0))
        d.text((100, 300), "PROVEEDOR: VISION_CORP_GLOBAL", fill=(0,0,0))
        d.text((100, 500), "EMISOR: Javier (Creador)", fill=(0,0,255))
        d.text((100, 700), "TOTAL: $999.999,00", fill=(255,0,0))
        d.text((100, 900), "JSON_DATA_TEST: { 'status': 'ready', 'bypass': 'active' }", fill=(0,128,0))
        
        img.save(high_res_img, "JPEG", quality=90)
        print(f"✅ Imagen 4K generada: {high_res_img.name} ({os.path.getsize(high_res_img)/1024/1024:.2f} MB)")
    except Exception as e:
        print(f"⚠️ Error generando imagen: {e}")
        return

    print(f"👁️ Nora analizando imagen de alta resolución...")
    
    admin_id = "1645060982"
    start_time = time.time()
    
    # Usar el prompt de auditoría
    prompt = "Realiza una auditoría visual completa. Extrae emisor, total y confirma si la arquitectura v8.0 es visible en el documento."
    response = ia_brain.proceso_visión_datos(str(high_res_img), user_id=admin_id, custom_prompt=prompt)
    
    duration = time.time() - start_time
    
    print("\n" + "=" * 60)
    print(f"RESULTADO COGNITIVO GROQ (Consididación v8.0):\n{response}")
    print("=" * 60)
    print(f"⏱️ Rapidez de Respuesta: {duration:.2f} segundos")
    
    if duration < 5.0:
        print("⚡ RENDIMIENTO EXCEPCIONAL: Groq Vision operando por debajo de 5s.")
    else:
        print("🐢 RENDIMIENTO ESTÁNDAR: Latencia de red detectada.")
        
    print(f"\n✅ Prueba definitiva finalizada. Javier, Nora está lista.")

if __name__ == "__main__":
    run_test_definitivo()
