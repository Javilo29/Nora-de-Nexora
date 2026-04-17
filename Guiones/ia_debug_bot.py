# Proyecto: Nora de Nexora - MyJNexoraVisual
import os
import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"D:\AGENTE_IA\.env")

TOKEN = os.environ.get("TELEGRAM_TOKEN")
ADMIN_ID = os.environ.get("TELEGRAM_ADMIN_ID", "").strip()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("NoraDebug")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    incoming_id = str(update.effective_user.id)
    print(f"DEBUG: Mensaje de {incoming_id} (Admin configurado: {ADMIN_ID})")
    
    if incoming_id == ADMIN_ID:
        await update.message.reply_text(f"✅ ¡Hola Jefe! Nora Debugger en línea. Tu ID es {incoming_id}.")
    else:
        logger.warning(f"🚫 Acceso denegado para {incoming_id}")

async def post_init(application):
    if ADMIN_ID and TOKEN:
        try:
            await application.bot.send_message(chat_id=ADMIN_ID, text="🧪 Nora Link: Test de Conectividad OK.")
            print(f"✅ Notificación de arranque enviada a {ADMIN_ID}")
        except Exception as e:
            print(f"❌ Error al enviar notificación: {e}")

def run():
    print(f"🚀 Iniciando Debug Bot...")
    print(f"ID Autorizado: [{ADMIN_ID}]")
    if not TOKEN: 
        print("❌ Error: No hay TOKEN.")
        return
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler('start', start))
    app.run_polling()

if __name__ == '__main__':
    run()
