"""
Nora v11.1 - Bot Simple para Render
Punto de entrada único y mínimo. Sin voz, sin watchdog, sin dependencias rotas.
"""
import os
import logging
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from io import BytesIO
from Guiones.ia_brain import procesar_con_groq, detectar_intencion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
PORT = int(os.getenv("PORT", 10000))
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://myjnexoravisual.onrender.com")

app = Flask(__name__)
bot = Bot(token=TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 Nora v11.1 operativa en Render. Enviame una foto de factura.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Imagen recibida. Analizando en RAM...")
    try:
        file = await update.message.photo[-1].get_file()
        response = requests.get(file.file_path)
        response.raise_for_status()
        
        imagen_ram = BytesIO(response.content)
        imagen_ram.seek(0)
        
        resultado = procesar_con_groq(imagen_ram)
        await update.message.reply_text(f"📋 Resultado:\n{resultado}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)[:200]}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    intencion = detectar_intencion(texto)
    
    if intencion == "saludo":
        await update.message.reply_text("Hola Javi. Nora v11.1 operativa.")
    elif intencion == "estado":
        await update.message.reply_text("✅ Sistema estable. Visión 100% RAM.")
    else:
        await update.message.reply_text(f"📝 Recibido: {texto}")

@app.route(f"/webhook", methods=["POST"])
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