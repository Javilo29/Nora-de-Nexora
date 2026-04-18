import os
import logging
import requests
from io import BytesIO
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from Guiones.ia_brain import procesar_con_groq, detectar_intencion

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
hablar_callback = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 Nora v11.1 operativa. Enviame una foto de una factura para analizar.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Imagen recibida. Analizando en RAM...")
    
    try:
        file = await update.message.photo[-1].get_file()
        file_url = file.file_path
        
        response = requests.get(file_url)
        response.raise_for_status()
        
        imagen_en_ram = BytesIO(response.content)
        imagen_en_ram.seek(0)
        
        resultado = procesar_con_groq(imagen_en_ram)
        await update.message.reply_text(f"📋 Resultado:\n{resultado}")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error en visión: {str(e)[:200]}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    intencion = detectar_intencion(texto)
    
    if intencion == "saludo":
        await update.message.reply_text("Hola Javi. Estoy operativa en la nube.")
    elif intencion == "estado":
        await update.message.reply_text("Sistema estable. Memoria compartida activa.")
    else:
        await update.message.reply_text(f"Recibido: {texto}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    webhook_url = f"https://myjnexoravisual.onrender.com/webhook"
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        url_path="webhook",
        webhook_url=webhook_url
    )
    
    logging.info("Nora v11.1 (100% RAM) corriendo en Render.")

if __name__ == "__main__":
    main()