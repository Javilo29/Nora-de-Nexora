# -*- coding: utf-8 -*-
# Proyecto: Nora de Nexora - Módulo WhatsApp Meta Cloud API v8.0
import os
import requests
import json
import logging
from pathlib import Path

# Configuración de Logs
logger = logging.getLogger("NoraWhatsApp")

# Credenciales (Se cargarán desde .env en el siguiente paso)
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_ID = os.environ.get("WHATSAPP_PHONE_ID")
WHATSAPP_API_URL = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages" if PHONE_ID else None

class NoraWhatsApp:
    def __init__(self):
        self.enabled = True if WHATSAPP_TOKEN and PHONE_ID else False
        if not self.enabled:
            print("⚠️ WhatsApp Meta Cloud API: Credenciales no configuradas.")
        else:
            print("📱 WhatsApp Meta Cloud API v8.0 Inicializado.")

    def send_message(self, to_number, text):
        """Envía un mensaje de texto vía WhatsApp API."""
        if not self.enabled:
            print("❌ Error: WhatsApp no está configurado.")
            return False

        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": text}
        }

        try:
            response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
            response_data = response.json()
            if response.status_code == 200:
                print(f"✅ Mensaje enviado a {to_number}")
                return True
            else:
                print(f"❌ Error WhatsApp API: {response_data}")
                return False
        except Exception as e:
            print(f"⚠️ Excepción en envío WhatsApp: {e}")
            return False

    def onboarding_client(self, name, phone):
        """Inicia el proceso de Onboarding de un nuevo cliente."""
        msg = (
            f"Hola {name}, soy Nora de Nexora. 🧠\n\n"
            "He sido activada para tu gestión contable y administrativa. "
            "Estoy integrando tus datos a la arquitectura v8.2.\n\n"
            "¿Podrías enviarme una foto de tu última factura para auditoría?"
        )
        return self.send_message(phone, msg)

    def handle_webhook_verification(self, token_recibido):
        """Valida el Webhook con Meta Cloud API."""
        verify_token = os.environ.get("VERIFY_TOKEN", "Nexora_Soberania_Digital_2026")
        if token_recibido == verify_token:
            return True
        return False

    def process_incoming_message(self, data):
        """Procesa el JSON entrante de WhatsApp y extrae el mensaje."""
        try:
            entry = data.get("entry", [{}])[0]
            change = entry.get("changes", [{}])[0]
            value = change.get("value", {})
            message = value.get("messages", [{}])[0]
            
            from_number = message.get("from")
            text_body = message.get("text", {}).get("body", "")
            
            if from_number and text_body:
                print(f"📥 [WhatsApp]: Mensaje de {from_number}: {text_body}")
                # Enviar al cerebro multinodal
                import ia_brain
                response = ia_brain.chat_with_nora(text_body, user_id=from_number, channel="whatsapp")
                self.send_message(from_number, response)
                return True
        except Exception as e:
            print(f"⚠️ Error procesando mensaje WhatsApp: {e}")
        return False

# Instancia global
nora_wa = NoraWhatsApp()

if __name__ == "__main__":
    # Prueba de estructura
    if nora_wa.enabled:
        print("🚀 Listo para enviar mensajes.")
    else:
        print("🚩 Configure WHATSAPP_TOKEN y WHATSAPP_PHONE_ID en .env")
