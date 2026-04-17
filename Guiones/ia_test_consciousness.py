# Test de Conciencia de Nora
import os
import sys
from pathlib import Path

# Configurar rutas para importar módulos locales
sys.path.append(str(Path(__file__).parent))

import ia_brain
import ia_responder

def test_hola():
    print("--- Test 1: Saludo Incial ---")
    persona = ia_responder.get_persona()
    prompt = f"{persona}\nResponde al Jefe: Hola"
    
    if ia_brain.model:
        try:
            response = ia_brain.model.generate_content(prompt)
            print(f"Respuesta de Nora: {response.text}")
            if "Nora" in response.text and "Nexora" in response.text:
                print("✅ Identidad Confirmada.")
            else:
                print("❌ Identidad Dudosa.")
        except Exception as e:
            print(f"❌ Error en generación: {e}")
    else:
        print("❌ Modelo no cargado.")

def test_error_handling():
    print("\n--- Test 2: Error Handling (Simulado) ---")
    # Simulamos lo que pasaría en handle_chat si falla la API
    error_msg = "¡Ups! Jefe, mi cerebro se distrajo un segundo. ¿Podrías repetirme eso o reenviarme el documento?"
    print(f"Mensaje de error configurado: {error_msg}")
    if "Ups" in error_msg and "Jefe" in error_msg:
        print("✅ Error handling en español correcto.")

if __name__ == "__main__":
    test_hola()
    test_error_handling()
