# Proyecto: Nora de Nexora - MyJNexoraVisual
# Módulo: Telegram Bot Link v7.5.5 SRE (Saneamiento de Rutas y Voz)
import os
import logging
import traceback
import asyncio
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from ia_paths import INBOX_DIR, LOGS_DIR, VISION_HISTORY_DIR
import ia_local_store
import ia_brain

# Configuración de Logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Roles y Permisos (Identidad Javier)
ADMIN_ID = "1645060982"
FAMILIA_ID = "7911365716"

# Callback para voz (main.py lo inyecta)
hablar_callback = None

async def security_check(update: Update):
    """Filtro de seguridad para asegurar obediencia al Creador."""
    uid = str(update.effective_user.id)
    if uid not in [ADMIN_ID, FAMILIA_ID]:
        await update.message.reply_text("⛔ Acceso restringido. Nora solo responde al Holding MyJNexoraVisual.")
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if uid == ADMIN_ID:
        saludo = "Javi, estoy aquí. Ya dejé atrás la rigidez. ¿A qué hito de negocio le vamos a dedicar nuestro genio hoy?"
    elif uid == FAMILIA_ID:
        saludo = "Es un honor saludarle. Nora a su disposición con total calidez."
    else:
        saludo = "Bienvenida/o a Nexora. Soy Nora, Directora de Operaciones."
    await update.message.reply_text(saludo)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesamiento visual con rutas de grado SRE."""
    if not await security_check(update): return
    
    uid = str(update.effective_user.id)
    await update.message.reply_text("Imagen recibida. Procedo con el análisis de los datos...")
    
    try:
        photo = update.message.photo[-1]
        new_file = await photo.get_file()
        # Saneamiento v7.5.5 SRE: Forzar resolución absoluta de ruta
        file_path = (VISION_HISTORY_DIR / f"img_{photo.file_unique_id}.jpg").resolve()
        await new_file.download_to_drive(str(file_path))
        
        response = ia_brain.proceso_visión_datos(str(file_path), user_id=uid)
        await update.message.reply_text(response)
        
        if uid == ADMIN_ID and hablar_callback:
            if "interrupción técnica" not in response.lower():
                hablar_callback("Análisis completado con éxito, Javier")
            else:
                hablar_callback("Javier, el flujo visual ha tenido una interrupción técnica, por favor reintente")
    except Exception as e:
        logger.error(f"Error en handle_photo: {e}")
        traceback.print_exc()
        await update.message.reply_text("🧠 [Nora v7.5.5 SRE]: Error físico al descargar imagen. Reintente.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja PDFs y documentos con auditoría absoluta."""
    if not await security_check(update): return
    uid = str(update.effective_user.id)
    
    doc = update.message.document
    if doc.mime_type == 'application/pdf' or doc.file_name.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
        await update.message.reply_text("📑 Analizando documento para auditoría v7.5.5 SRE...")
        new_file = await doc.get_file()
        file_path = (INBOX_DIR / doc.file_name).resolve()
        await new_file.download_to_drive(str(file_path))
        
        response = ia_brain.proceso_visión_datos(str(file_path), user_id=uid)
        await update.message.reply_text(response)
        
        if uid == ADMIN_ID and hablar_callback:
            if "interrupción técnica" not in response.lower():
                hablar_callback("Análisis completado con éxito, Javier")
    else:
        await update.message.reply_text("Solo analizo PDFs o imágenes para auditoría contable.")

async def handle_video_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Videomensajes: Extracción de Keyframes con rutas SRE."""
    if not await security_check(update): return
    uid = str(update.effective_user.id)
    await update.message.reply_text("🎬 Procesando videomensaje (Extrayendo fotogramas clave)...")
    
    vn = update.message.video_note
    new_file = await vn.get_file()
    video_path = (INBOX_DIR / f"vn_{vn.file_unique_id}.mp4").resolve()
    await new_file.download_to_drive(str(video_path))
    
    # Extraer fotogramas
    frames = ia_brain.extract_keyframes(str(video_path))
    if not frames:
        await update.message.reply_text("No pude extraer cuadros del video.")
        return
        
    response = ia_brain.proceso_visión_datos(frames, user_id=uid)
    await update.message.reply_text(response)
    
    if uid == ADMIN_ID and hablar_callback:
        if "interrupción técnica" not in response.lower():
            hablar_callback("Análisis completado con éxito, Javier")

async def handle_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chat reflexivo multimodal v7.5.5 SRE."""
    if not await security_check(update): return
    
    user_text = update.message.text
    uid = str(update.effective_user.id)
    print(f"📥 [Nora SRE]: Mensaje recibido de {uid}: {user_text}")
    
    try:
        # v8.2: Hilos independientes mediante user_id
        response = ia_brain.chat_with_nora(user_text, user_id=uid, channel="telegram")
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error en handle_chat: {e}")
        traceback.print_exc()
        await update.message.reply_text(f"Javi, error de enlace cognitivo en el hilo {uid}. Reintente.")

async def send_ignition_report(application: Application):
    """Reporte de ignición v8.1 - Socia de Javier."""
    msg = "Javi, estoy aquí. Ya dejé atrás la rigidez. ¿A qué hito de negocio le vamos a dedicar nuestro genio hoy?"
    try:
        await application.bot.send_message(chat_id=ADMIN_ID, text=msg)
        print(f"✨ [Ignición v8.1]: Mensaje enviado a Javi.")
    except Exception as e:
        print(f"⚠️ Fallo al enviar reporte de ignición: {e}")

def run_bot():
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        print("❌ TELEGRAM_TOKEN no encontrado en .env")
        return

    app = Application.builder().token(token).post_init(send_ignition_report).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.VIDEO_NOTE, handle_video_note))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_chat))
    
    print(f"🚀 Nora Link v8.0 SRE escuchando... Admin: {ADMIN_ID}")
    app.run_polling()

if __name__ == '__main__':
    run_bot()
