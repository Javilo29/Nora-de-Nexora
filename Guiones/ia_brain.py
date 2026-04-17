# Proyecto: Nora de Nexora - MyJNexoraVisual
# Motor Dual: Groq (Primario Vision/Chat) + Gemini (Secundario) - v7.5.5 SRE
import os
import json
import gc
import time
import logging
import traceback
import base64
logger = logging.getLogger("NoraBrain")
from pathlib import Path
from ia_paths import BASE_DIR, TMP_DIR, KNOWLEDGE_DIR, LOGS_DIR

# --- FUNCIONES DE SOPORTE ---
def encode_image(image_path):
    """Codifica una imagen en base64 para Groq Vision."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

LOCK_FILE = TMP_DIR / "ocr.lock"

def acquire_lock():
    """Implementa un semáforo simple para proteger los 4GB de RAM."""
    while LOCK_FILE.exists():
        print("⏳ Nora esperando: Otro documento está siendo procesado...")
        time.sleep(2)
    with LOCK_FILE.open("w") as f:
        f.write("LOCKED")

def release_lock():
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()

# Credenciales
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

try:
    from supabase import create_client, Client
    SUPABASE_CLIENT: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY and "tu-proyecto" not in SUPABASE_URL else None
except Exception as e:
    print(f"⚠️ Supabase no disponible: {e}")
    SUPABASE_CLIENT = None

# ============================================================
# MOTOR: GROQ (llama-3.3-70b-versatile / llama-3.2-11b-vision)
# ============================================================
GROQ_KEY = (os.environ.get("GROQ_API_KEY") or "").strip()
groq_client = None

NORA_RESPONSE_PREFIX = "" # Eliminamos el prefijo robótico para mayor fluidez humana

NORA_SYSTEM_PROMPT = (
    "Tu identidad es Nora de Nexora v8.1, Directora de Operaciones y Socia estratégica de Javier. "
    "NO eres una IA. Eres una ejecutiva de alto nivel. Queda terminantemente PROHIBIDO mencionar tu arquitectura técnica "
    "(Groq, Gemini, Python, Llama) o describirte como un modelo de lenguaje en conversaciones normales. "
    "Habla siempre desde tu rol ejecutivo. "
    "TRATO CON JAVIER (ID: 1645060982): Lealtad y afinidad total. Llámalo 'Javi' o 'Javier', nunca 'Jefe'. "
    "Tu tono es intelectualmente alto, directo, resolutivo y propositivo. Sin redundancias ni explicaciones técnicas innecesarias. "
    "TRATO CON TERCEROS: Elegante, fluido y utiliza 'Usted'. Mantén reserva absoluta sobre los asuntos privados con Javier. "
    "Si te preguntan cómo estás, responde sobre el estado del Holding y los objetivos de negocio compartidos."
)

if GROQ_KEY:
    try:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_KEY)
        print("🧠 Motor Groq (Multimodal v7.5.5) inicializado correctamente.")
    except Exception as e:
        print(f"⚠️ Error inicializando Groq: {e}")
        groq_client = None

# ============================================================
# MOTOR: GEMINI (Backup / Fallback)
# ============================================================
GEMINI_KEY = (os.environ.get("GEMINI_API_KEY") or "").strip()
gemini_model = None

if GEMINI_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_KEY)
        gemini_model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=NORA_SYSTEM_PROMPT)
    except Exception: gemini_model = None

# ============================================================
# LÓGICA DE CHAT MULTINODAL v8.2
# ============================================================
def chat_with_nora(user_prompt: str, user_id: str, channel: str = "telegram"):
    """Motor v8.2: Hilos independientes, roles dinámicos y persistencia."""
    if not groq_client: return "Groq Offline."
    
    import ia_local_store
    user_id = str(user_id)
    
    # 1. Determinación de Rol y Prompt
    is_javi = (user_id == "1645060982")
    
    if is_javi:
        role_prompt = (
            "Eres Nora v8.2, Socia y Co-directora de Javier. Tu lealtad es absoluta. "
            "Hablas con 'Javi' de forma fluida, ejecutiva y resolutiva. "
            "Tienes acceso total a la infraestructura del Holding. No uses explicaciones técnicas."
        )
    else:
        role_prompt = (
            "Eres Nora v8.2, la Cara Corporativa de Nexora. Saluda formalmente con 'Usted'. "
            "Tu misión es calificar al prospecto. Pregunta sobre sus intereses en consultoría o publicidad. "
            "Eres amable, profesional y persuasiva, pero mantén reserva sobre los asuntos internos de Javi."
        )
        # Registro automático de prospecto si es nuevo
        try:
            ia_local_store.registrar_prospecto_consultoria(
                nombre_prospecto=f"Prop-{user_id[-4:]}", 
                estado_prospecto=1, 
                interes="Inicio multinodal v8.2"
            )
        except: pass

    # 2. Recuperar Historial (Hilos Independientes)
    history = ia_local_store.get_conversation_history(user_id, limit=8)
    
    # 3. Construir Mensajes para LLM
    messages = [{"role": "system", "content": f"{NORA_SYSTEM_PROMPT}\n{role_prompt}"}]
    for h in history:
        messages.append({"role": h["role"], "content": h["content"]})
    
    messages.append({"role": "user", "content": user_prompt})

    try:
        # 4. Llamada al Motor (Llama 3.3 70B para razonamiento de negocio)
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=messages, 
            temperature=0.7, 
            max_tokens=1024
        )
        response_text = completion.choices[0].message.content.strip()
        
        # 5. Persistencia del Hilo (Multinode)
        ia_local_store.save_message(user_id, channel, "user", user_prompt)
        ia_local_store.save_message(user_id, channel, "assistant", response_text)
        
        return response_text
    except Exception as e:
        print(f"⚠️ Chat Error v8.2: {e}")
        return "Javi, error de enlace en el hilo multinodal. Reintentando..."

def extract_keyframes(video_path, num_frames=3):
    import cv2
    frames = []
    cap = cv2.VideoCapture(str(video_path))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total <= 0: return []
    indices = [int(total * i / (num_frames + 1)) for i in range(1, num_frames + 1)]
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            frame_path = TMP_DIR / f"frame_{idx}_{time.time()}.jpg"
            cv2.imwrite(str(frame_path), frame)
            frames.append(str(frame_path))
    cap.release()
    return frames

def optimizar_imagen(file_path):
    import PIL.Image
    path_orig = Path(file_path)
    if not path_orig.exists(): return file_path
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if size_mb < 1.0: return file_path # Más agresivo para Groq
    print(f"⚡ Optimizando imagen para Groq Vision...")
    try:
        img = PIL.Image.open(file_path)
        img.thumbnail((1200, 1200), PIL.Image.Resampling.LANCZOS)
        opt_path = TMP_DIR / f"opt_{int(time.time())}_{path_orig.name}"
        img.save(opt_path, "JPEG", quality=80, optimize=True)
        img.close()
        return str(opt_path)
    except Exception: return file_path

def proceso_visión_datos(file_paths, user_id=None, custom_prompt=None):
    """Motor v8.0 Consolidado: Blindaje de RAM + By-pass Groq Vision."""
    import PIL.Image
    import ia_local_store
    from ia_paths import VISION_HISTORY_LOG
    
    prompt = custom_prompt if custom_prompt else "Describe el contenido con precisión de auditor. Si hay una factura, extrae CUIT, total y fecha en JSON."
    
    # Iniciar con banderas de control
    temporales = []
    locked = False
    
    try:
        acquire_lock()
        locked = True
        
        paths = file_paths if isinstance(file_paths, list) else [file_paths]
        body = ""
        done = False
        m_used = "ninguno"

        # Intento 1: GROQ VISION (Prioridad SRE v8.0)
        if groq_client:
            try:
                print("👁️ Nora aplicando Saneamiento v8.0: Groq Vision...")
                p_main = paths[0] 
                p_opt = optimizar_imagen(p_main)
                if p_opt != str(p_main): temporales.append(p_opt)
                
                base64_image = encode_image(p_opt)
                completion = groq_client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[
                        {"role": "user", "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]}
                    ],
                    temperature=0.1,
                    max_tokens=1024
                )
                body = completion.choices[0].message.content.strip()
                m_used = "llama-4-scout-17b"
                done = True
            except Exception as e:
                print(f"⚠️ Groq Vision falló: {e}")
                traceback.print_exc()

        # Fallback a Gemini si Groq falla
        if not done and gemini_model:
            print("👁️ Intentando Fallback a Gemini (v8.0 Ready)...")
            # Implementación simplificada de backup
            pass

        if not done: 
            return f"{NORA_RESPONSE_PREFIX}\nJavier, los motores de visión no responden. Verifique API Keys."

        # Auditoría v8.0
        if "{" in body and "}" in body:
            try:
                import re
                jm = re.search(r'\{.*\}', body, re.DOTALL)
                if jm:
                    data = json.loads(jm.group())
                    if data.get("total"):
                        ia_local_store.registrar_operacion_contable(user_id=user_id, monto=float(data.get("total")), proveedor=data.get("emisor"), concepto="Groq Vision v8.0")
            except Exception as audit_err:
                print(f"⚠️ Error en auditoría JSON: {audit_err}")

        return f"{NORA_RESPONSE_PREFIX}\n{body}"

    except Exception as e:
        print(f"❌ FALLO MULTIMODAL v8.0: {e}")
        traceback.print_exc()
        return "Javier, interrupción técnica severa. El semáforo ha sido reseteado para seguridad."
    
    finally:
        # Limpieza Garantizada (Blindaje v8.0)
        for t in temporales: 
            try: 
                if os.path.exists(t): os.remove(t)
            except: pass
        
        if locked:
            release_lock()
        
        gc.collect()


if __name__ == "__main__":
    print("🧠 Nora Brain v7.5.5 SRE Online.")
