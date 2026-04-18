import os
import logging
import requests
from io import BytesIO
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from Guiones.NoraCore.nora_brain import NoraBrain
from Guiones.NoraCore.nora_vision import NoraVision

# Configuración
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 10000))
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "")

# Instancias del Core
brain = NoraBrain()
vision = NoraVision()

app = Flask(__name__)
bot = Bot(token=TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = brain.get_response(update.effective_user.id, "Hola, presentate.")
    await update.message.reply_text(response)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Veo que me pasaste una imagen. Dejame analizarla...")
    try:
        file = await update.message.photo[-1].get_file()
        response = requests.get(file.file_path)
        img_bytesio = BytesIO(response.content)
        
        # Usar módulo de visión
        resultado = vision.analizar_factura(img_bytesio)
        
        if "error" in resultado:
            await update.message.reply_text(f"❌ No pude procesar la imagen: {resultado['error']}")
        else:
            msg = (f"✅ Análisis completado:\n"
                   f"📋 CUIT: {resultado.get('cuit', 'N/A')}\n"
                   f"💰 Importe: ${resultado.get('importe', 'N/A')}\n"
                   f"📅 Fecha: {resultado.get('fecha', 'N/A')}\n"
                   f"📄 Tipo: {resultado.get('tipo', 'N/A')}")
            await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ Error técnico: {str(e)}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    
    # El cerebro procesa el mensaje
    response = brain.get_response(user_id, user_text)
    await update.message.reply_text(response)

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Nora Cloud Bot Operational", 200

if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Si hay RENDER_URL, usamos webhook. Si no, polling (para desarrollo local).
    if RENDER_URL:
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path="webhook",
            webhook_url=f"{RENDER_URL}/webhook"
        )
    else:
        logger.info("Iniciando en modo POLLING (Local)...")
        application.run_polling()
