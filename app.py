"""
NORA v12.3 FINAL - FPS.ms Ready
Modo Polling 24/7 - Sin Flask - Sin Webhooks
"""
import os
import logging
import json
import base64
from io import BytesIO
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from PIL import Image
from groq import Groq

# Configuración
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FPS.ms usa BOT_TOKEN (no TELEGRAM_TOKEN)
TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

groq_client = Groq(api_key=GROQ_API_KEY)

# FAQ Local (Ahorro de Tokens)
FAQ_RESPUESTAS = {
    "servicios": "En Nexora Visual ofrecemos soluciones de IA para automatización administrativa y comercial. ¿Le gustaría agendar una demo con nuestro equipo?",
    "contacto": "Puede comunicarse con nuestro equipo comercial al email contacto@nexoravisual.com o visitar nuestra web.",
    "precio": "Nuestros planes se adaptan al tamaño de su negocio. ¿Le gustaría que un asesor le comparta los planes vigentes?",
    "ayuda": "Soy Nora, su asistente virtual. Puedo ayudarle a procesar facturas, recordarle tareas o responder consultas sobre Nexora Visual."
}

# Memoria Multi-Cliente
memoria_usuarios = {}

# Prompt del Sistema
NORA_SYSTEM_PROMPT = """
Eres Nora, la Asistente Virtual Oficial de Nexora Visual. 
Tu tono es profesional, ejecutivo y amable. Hablas español neutro.
Tu objetivo es asistir en la gestión de facturas, recordatorios y consultas administrativas.
No inventes información. Si no sabes algo, dices: 'Permítame consultarlo con el equipo de Nexora Visual'.
Mantén las respuestas concisas (máximo 2-3 líneas).
"""

# --- FUNCIONES DE VISIÓN (100% RAM) ---
def encode_image_from_bytesio(img_bytesio):
    img_bytesio.seek(0)
    return base64.b64encode(img_bytesio.read()).decode('utf-8')

def optimizar_imagen_en_ram(img_bytesio, max_size=1024):
    img_bytesio.seek(0)
    img = Image.open(img_bytesio)
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    output = BytesIO()
    img.save(output, format='JPEG', quality=85)
    output.seek(0)
    return output

def procesar_imagen_con_groq(img_bytesio):
    try:
        img_optimizada = optimizar_imagen_en_ram(img_bytesio)
        img_base64 = encode_image_from_bytesio(img_optimizada)
        prompt = """
Analizá esta imagen de factura o ticket.
Devolvé UNICAMENTE un JSON válido con este formato:
{"cuit": "xx-xxxxxxxx-x", "importe": numero, "fecha": "dd/mm/aaaa"}
Si no podés leer algún dato, usá null.
"""
        completion = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
            ]}],
            temperature=0.1, max_tokens=200
        )
        return json.loads(completion.choices[0].message.content.strip())
    except Exception as e:
        logger.error(f"Error Visión: {e}")
        return {"cuit": None, "importe": None, "fecha": None, "error": str(e)}

# --- FUNCIÓN DE CONVERSACIÓN ---
def conversar_con_nora(mensaje, chat_id):
    for clave, respuesta in FAQ_RESPUESTAS.items():
        if clave in mensaje.lower():
            return respuesta

    if chat_id not in memoria_usuarios:
        memoria_usuarios[chat_id] = []
    
    historial = memoria_usuarios[chat_id]
    historial.append({"role": "user", "content": mensaje})
    
    if len(historial) > 8:
        historial = historial[-6:]
        memoria_usuarios[chat_id] = historial

    try:
        messages = [{"role": "system", "content": NORA_SYSTEM_PROMPT}] + historial
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )
        respuesta = completion.choices[0].message.content.strip()
        historial.append({"role": "assistant", "content": respuesta})
        memoria_usuarios[chat_id] = historial
        return respuesta
    except Exception as e:
        logger.error(f"Error Groq Texto: {e}")
        return "Disculpe las molestias. Estoy experimentando una alta demanda. ¿Podría repetir su consulta en un momento?"

# --- HANDLERS DE TELEGRAM ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Buenos días. Soy Nora, asistente virtual de Nexora Visual. ¿En qué puedo asistirle hoy?")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Procesando documento fiscal...")
    try:
        file = await update.message.photo[-1].get_file()
        response = requests.get(file.file_path)
        img_bytesio = BytesIO(response.content)
        datos = procesar_imagen_con_groq(img_bytesio)
        
        if datos.get("error"):
            await update.message.reply_text("❌ No se pudo leer el documento. Por favor, asegúrese de que la imagen sea clara.")
        else:
            respuesta = f"📋 **Documento Procesado:**\n• CUIT: {datos.get('cuit', 'N/A')}\n• Importe: ${datos.get('importe', 'N/A')}\n• Fecha: {datos.get('fecha', 'N/A')}"
            await update.message.reply_text(respuesta)
    except Exception as e:
        await update.message.reply_text("❌ Error interno al procesar la imagen.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    texto = update.message.text
    
    texto_lower = texto.lower().strip()
    if texto_lower in ["gracias", "ok", "perfecto", "de acuerdo", "listo"]:
        await update.message.reply_text("Es un placer asistirle. Estamos a un mensaje de distancia.")
        return
        
    respuesta = conversar_con_nora(texto, chat_id)
    await update.message.reply_text(respuesta)

# --- ARRANQUE PARA FPS.ms (POLLING) ---
if __name__ == "__main__":
    print(f"🔥 Nora v12.3 arrancando en FPS.ms (Polling 24/7)...", flush=True)
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    logger.info("🚀 Nora v12.3 | Modo Polling | FPS.ms Ready")
    print("✅ Nora está VIVA y escuchando...", flush=True)
    
    # FPS.ms usa POLLING, no webhooks
    application.run_polling()