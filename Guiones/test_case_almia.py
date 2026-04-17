import os
import json
import ia_brain
import ia_responder

# Datos del Caso Real proporcionados por el usuario
CASE_TEXT = "CLIENTE MARIA ITATI PALACIO, Salida-00001002, TOTAL $ 14.500,00, Artículos: Pañuelo, Alpargatas, Sombrero"
CLIENT_NAME = "Maria Itati Palacio"
IS_EDUCATIONAL = True # Probaremos el flujo educativo solicitado
TO_EMAIL = "maria@ejemplo.com"

def simulate_almia_clothes_case():
    print("🚀 Simulando Caso Real: ALMIA CLOTHES")
    
    # 1. Análisis de Nora (Brain)
    # Le pasamos el texto directamente ya que Nora ahora acepta texto o path
    analysis = ia_brain.analyze_document_with_vision(CASE_TEXT)
    
    print(f"Análisis Técnico: {json.dumps(analysis, indent=2)}")
    
    # 2. Respuesta de Nora (Responder)
    # Simulamos el estado obtenido del cerebro
    status = analysis.get("estado_verificacion")
    
    # En un caso real, esto se recuperaría de la DB tras la inserción
    ia_responder.process_feedback(
        cliente_id="CLIENT-001", 
        client_name=CLIENT_NAME, 
        is_educational=IS_EDUCATIONAL, 
        doc_type=status, 
        filename="Comprobante_Almia_Clothes.txt", 
        to_email=TO_EMAIL
    )

if __name__ == "__main__":
    simulate_almia_clothes_case()
