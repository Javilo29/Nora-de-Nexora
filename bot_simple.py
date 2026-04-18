"""
Nora v11.1 - Bot Ultra Simple para Render
Cero dependencias internas. Solo usa librerías estándar + telegram + groq.
"""
import os
import logging
import json
import base64
from io import BytesIO
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from PIL import Image
from groq import Groq

# Configuración
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
PORT = int(os.getenv("PORT", 10000))
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://myjnexoravisual.onrender.com")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Cliente Groq
groq_client = Groq(api_key=GROQ_API_KEY)

app = Flask(__name__)
bot = Bot(token=TOKEN)

# ------------------------------------------------------------
# FUNCIONES DE VISIÓN (100% RAM, SIN DEPENDENCIAS EXTERNAS)
# ------------------------------------------------------------

def encode_image_from_bytesio(img_bytesio):
    """Convierte BytesIO a base64 para Groq."""
    img_bytesio.seek(0)
    return base64.b64encode(img_bytesio.read()).decode('utf-8')

def optimizar_imagen_en_ram(img_bytesio, max_size=1024):
    """Redimensiona imagen en RAM para ahorrar tokens."""
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
    """Envía imagen a Groq Vision y devuelve JSON con CUIT, importe, fecha."""
    try:
        img_optimizada = optimizar_imagen_en_ram(img_bytesio)
        img_base64 = encode_image_from_bytesio(img_optimizada)
        
        prompt = """
Eres Nora v11.1, un sistema de visión artificial. Analizá esta imagen de factura o ticket.
Devolvé UNICAMENTE un JSON válido con este formato exacto:
{"cuit": "xx-xxxxxxxx-x", "importe": numero, "fecha": "dd/mm/aaaa"}

Si no podés leer algún dato, usá null.
No agregues texto adicional. Solo el JSON.
"""
        
        completion = groq_client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                ]}
            ],
            temperature=0.1,
            max_tokens=200
        )
        
        respuesta = completion.choices[0].message.content.strip()
        # Intentar parsear JSON
        return json.loads(respuesta)
    except Exception as e:
        logger.error(f"Error en Groq: {e}")
        return {"error": str(e)[:100], "cuit": None, "importe": None, "fecha": None}

# ------------------------------------------------------------
# HANDLERS DE TELEGRAM
# ------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 Nora v11.1 operativa en Render. Enviame una foto de factura.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Imagen recibida. Analizando en RAM...")
    try:
        file = await update.message.photo[-1].get_file()
        response = requests.get(file.file_path)
        response.raise_for_status()
        
        img_bytesio = BytesIO(response.content)
        resultado = procesar_imagen_con_groq(img_bytesio)
        
        if "error" in resultado:
            await update.message.reply_text(f"❌ Error: {resultado['error']}")
        else:
            await update.message.reply_text(
                f"📋 CUIT: {resultado.get('cuit', 'N/A')}\n"
                f"💰 Importe: ${resultado.get('importe', 'N/A')}\n"
                f"📅 Fecha: {resultado.get('fecha', 'N/A')}"
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)[:200]}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()
    if "hola" in texto or "estado" in texto:
        await update.message.reply_text("✅ Nora v11.1 activa. Visión 100% RAM.")
    else:
        await update.message.reply_text("📝 Enviame una foto de factura para analizar.")

# ------------------------------------------------------------
# WEBHOOK Y SERVIDOR
# ------------------------------------------------------------

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Nora v11.1 Running", 200

if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=f"{RENDER_URL}/webhook"
    )
    
    logger.info(f"Nora v11.1 corriendo en {RENDER_URL}")
    app.run(host="0.0.0.0", port=PORT)