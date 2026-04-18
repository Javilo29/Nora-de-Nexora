# Proyecto: Nora de Nexora - MyJNexoraVisual
# Módulo: Telegram Bot Link v11.1 (Render Cloud) - Saneamiento de Rutas y Vision
import os
import logging
import traceback
import asyncio
import tempfile
import requests
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
        
        # Saneamiento v11.1: Usar tempfile para Render Cloud
        file_url = new_file.file_path
        img_res = requests.get(file_url)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(img_res.content)
            file_path = tmp_file.name
        
        try:
            response = ia_brain.proceso_visión_datos(str(file_path), user_id=uid)
            await update.message.reply_text(response)
            
            if uid == ADMIN_ID and hablar_callback:
                if "interrupción técnica" not in response.lower():
                    hablar_callback("Análisis completado con éxito, Javier")
                else:
                    hablar_callback("Javier, el flujo visual ha tenido una interrupción técnica, por favor reintente")
        finally:
            # Limpieza inmediata para ahorrar espacio en Render (1GB límite)
            if os.path.exists(file_path):
                os.unlink(file_path)
    except Exception as e:
        logger.error(f"Error en handle_photo: {e}")
        traceback.print_exc()
        await update.message.reply_text("🧠 [Nora v11.1 (Render Cloud)]: Error físico al descargar imagen. Reintente.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja PDFs y documentos con auditoría absoluta."""
    if not await security_check(update): return
    uid = str(update.effective_user.id)
    
    doc = update.message.document
    if doc.mime_type == 'application/pdf' or doc.file_name.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
        await update.message.reply_text("📑 Analizando documento para auditoría v11.1 (Render Cloud)...")
        new_file = await doc.get_file()
        
        file_url = new_file.file_path
        doc_res = requests.get(file_url)
        suffix = Path(doc.file_name).suffix or ".pdf"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(doc_res.content)
            file_path = tmp_file.name
        
        try:
            response = ia_brain.proceso_visión_datos(str(file_path), user_id=uid)
            await update.message.reply_text(response)
            
            if uid == ADMIN_ID and hablar_callback:
                if "interrupción técnica" not in response.lower():
                    hablar_callback("Análisis completado con éxito, Javier")
        finally:
            if os.path.exists(file_path):
                os.unlink(file_path)
    else:
        await update.message.reply_text("Solo analizo PDFs o imágenes para auditoría contable.")

async def handle_video_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Videomensajes: Extracción de Keyframes con rutas SRE."""
    if not await security_check(update): return
    uid = str(update.effective_user.id)
    await update.message.reply_text("🎬 Procesando videomensaje (Extrayendo fotogramas clave)...")
    
    vn = update.message.video_note
    new_file = await vn.get_file()
    
    file_url = new_file.file_path
    vn_res = requests.get(file_url)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
        tmp_file.write(vn_res.content)
        video_path = tmp_file.name
    
    try:
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
    finally:
        if os.path.exists(video_path):
            os.unlink(video_path)

async def handle_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chat reflexivo multimodal v11.1 (Render Cloud)."""
    if not await security_check(update): return
    
    user_text = update.message.text
    uid = str(update.effective_user.id)
    print(f"📥 [Nora SRE]: Mensaje recibido de {uid}: {user_text}")
    
    try:
        # v11.1: Hilos independientes con protocolo de intermediación
        result = ia_brain.chat_with_nora(user_text, user_id=uid, channel="telegram")
        response = result["response"]
        await update.message.reply_text(response)
        
        # Lógica de Notificación a Javier (ADMIN_ID)
        if result.get("notify_admin"):
            user_name = update.effective_user.first_name or uid
            summary = user_text
            aviso = f"📢 Javi, {user_name} me ha solicitado consultarte lo siguiente:\n\n\"{summary}\""
            await context.bot.send_message(chat_id=ADMIN_ID, text=aviso)
            print(f"📧 [Notificación]: Aviso de consulta enviado a Javi desde {uid}")
            
    except Exception as e:
        logger.error(f"Error en handle_chat: {e}")
        traceback.print_exc()
        await update.message.reply_text(f"Javi, error de enlace cognitivo en el hilo {uid}. Reintente.")

async def send_ignition_report(application: Application):
    """Reporte de ignición v11.1 - Socia de Javier."""
    msg = "Javi, estoy aquí. Ya dejé atrás la rigidez. ¿A qué hito de negocio le vamos a dedicar nuestro genio hoy?"
    try:
        await application.bot.send_message(chat_id=ADMIN_ID, text=msg)
        print(f"✨ [Ignición v11.1]: Mensaje enviado a Javi.")
    except Exception as e:
        print(f"⚠️ Fallo al enviar reporte de ignición: {e}")

def run_bot():
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        print("❌ TELEGRAM_TOKEN no encontrado en .env")
        return

    # Saneamiento v11.1: Limpiar webhook ANTES de iniciar
    import asyncio
    from telegram import Bot
    try:
        temp_bot = Bot(token=token)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(temp_bot.delete_webhook(drop_pending_updates=True))
        print("🧹 Webhook eliminado preventivamente.")
    except Exception as e:
        print(f"⚠️ Aviso: No se pudo eliminar webhook preventivamente: {e}")

    app = Application.builder().token(token).post_init(send_ignition_report).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.VIDEO_NOTE, handle_video_note))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_chat))
    
    print(f"🚀 Nora Link v11.1 escuchando... Admin: {ADMIN_ID}")
    app.run_polling()

if __name__ == '__main__':
    run_bot()
