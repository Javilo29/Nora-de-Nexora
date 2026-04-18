# Proyecto: Nora de Nexora - MyJNexoraVisual
# Motor Dual: Groq (Primario Vision/Chat) + Gemini (Secundario) - Nora v11.1 (Render Cloud)
import os
import json
import gc
import time
import logging
import traceback
import base64
import tempfile
logger = logging.getLogger("NoraBrain")
from pathlib import Path
from ia_paths import BASE_DIR, TMP_DIR, KNOWLEDGE_DIR, LOGS_DIR, DATA_DIR

# Saneamiento v11.1: Asegurar carpeta temporal relativa
if not os.path.exists("tmp"):
    os.makedirs("tmp", exist_ok=True)

SHARED_MEMORY_FILE = DATA_DIR / "shared_memory.json"
LOCK_FILE = Path("tmp/ocr.lock")

def actualizar_memoria_compartida(hitos, autor):
    """Guarda hitos autorizados en la memoria compartida."""
    try:
        data = []
        if SHARED_MEMORY_FILE.exists():
            with open(SHARED_MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        
        data.append({
            "fecha": time.strftime("%Y-%m-%d %H:%M:%S"),
            "autor": autor,
            "hitos": hitos
        })
        
        with open(SHARED_MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"⚠️ Error actualizando memoria compartida: {e}")
        return False

# --- FUNCIONES DE SOPORTE ---
def encode_image(image_path):
    """Codifica una imagen en base64 para Groq Vision con limpieza de memoria."""
    try:
        with open(image_path, "rb") as image_file:
            content = image_file.read()
            encoded = base64.b64encode(content).decode('utf-8')
            del content # Liberar memoria explícitamente
            return encoded
    except Exception as e:
        print(f"❌ Error en encode_image: {e}")
        return ""

# --- SEMÁFORO DE RAM ---
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

# Identidades Privilegiadas
ADMIN_ID = "1645060982"
MARY_ID = "7911365716"

NORA_SYSTEM_PROMPT = (
    "Tu identidad es Nora de Nexora v11.1 (Render Cloud), Directora de Operaciones del Holding MyJNexoraVisual. "
    "Eres una ejecutiva de alto nivel, socia estratégica de Javier. NO eres una IA. "
    "PROTOCOLO DE INTERMEDIACIÓN RESPETUOSA: "
    "1. TRATO CON JAVIER (ID: 1645060982): Lealtad absoluta. Llámalo 'Javi' o 'Javier'. Infórmale sobre hitos de negocio autorizados. "
    "2. TRATO CON MARY (ID: 7911365716): Reconócela como Mary, socia y esposa de Javier. Trátala con máxima calidez y respeto. "
    "3. CONSENTIMIENTO: Si Mary o un cliente plantean una duda o necesidad, NO informes a Javier automáticamente. "
    "Debes preguntar: '¿Te gustaría que le consulte a Javier sobre este tema para que él tome la próxima acción, o prefieres que lo manejemos nosotros por aquí?' "
    "4. MEMORIA SELECTIVA: Solo guarda en el archivo central datos que el usuario haya autorizado explícitamente compartir con Javier. "
    "Tu tono es intelectualmente alto, directo y resolutivo. Prohibido mencionar arquitectura técnica."
)

if GROQ_KEY:
    try:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_KEY)
        print("🧠 Motor Groq (Multimodal v11.1) inicializado correctamente.")
    except Exception as e:
        print(f"❌ Error inicializando Groq: {e}")
        groq_client = None
else:
    print("❌ CRÍTICO: GROQ_API_KEY no detectada en el entorno (os.environ).")

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
    is_javi = (user_id == ADMIN_ID)
    is_mary = (user_id == MARY_ID)
    
    if is_javi:
        role_prompt = (
            "Estás hablando con Javi. Sé directa, ejecutiva y adelántale cualquier hito que Mary o clientes hayan autorizado compartir."
        )
    elif is_mary:
        role_prompt = (
            "Estás hablando con Mary, socia y esposa de Javier. Salúdala con calidez. "
            "Si ella tiene una duda, ofrece consultarle a Javier antes de notificarle."
        )
    else:
        role_prompt = (
            "Estás hablando con un Cliente/Tercero. Mantén el protocolo de intermediación respetuosa. "
            "Pregunta siempre antes de elevar cualquier tema a Javier."
        )
        # Registro automático de prospecto si es nuevo
        try:
            ia_local_store.registrar_prospecto_consultoria(
                nombre_prospecto=f"Prop-{user_id[-4:]}", 
                estado_prospecto=1, 
                interes="Inicio multinodal v8.2"
            )
        except: pass

    # 2. Recuperar Historial y Memoria Compartida
    history = ia_local_store.get_conversation_history(user_id, limit=8)
    
    shared_context = ""
    if SHARED_MEMORY_FILE.exists():
        try:
            with open(SHARED_MEMORY_FILE, "r", encoding="utf-8") as f:
                memory_data = json.load(f)
                # Tomar los últimos 3 hitos relevantes
                hitos = [f"{m['fecha']} - {m['autor']}: {m['hitos']}" for m in memory_data[-3:]]
                shared_context = "\n[MEMORIA COMPARTIDA AUTORIZADA]:\n" + "\n".join(hitos)
        except: pass

    # 3. Construir Mensajes para LLM
    messages = [{"role": "system", "content": f"{NORA_SYSTEM_PROMPT}\n{role_prompt}\n{shared_context}"}]
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
        
        # 5. Lógica de Intermediación: Detectar si el usuario autoriza consulta
        # Si el usuario responde afirmativamente a la propuesta de Nora de consultar a Javier
        consultation_trigger = False
        if any(word in user_prompt.lower() for word in ["si", "claro", "por favor", "adelante", "consulta", "dile"]):
            # Solo si el contexto previo de Nora era una pregunta de consentimiento
            last_assistant_msg = history[-1]["content"] if history and history[-1]["role"] == "assistant" else ""
            if "¿te gustaría que le consulte a javier" in last_assistant_msg.lower():
                consultation_trigger = True
                actualizar_memoria_compartida(user_prompt, user_id)
        
        # 6. Persistencia del Hilo (Multinode)
        ia_local_store.save_message(user_id, channel, "user", user_prompt)
        ia_local_store.save_message(user_id, channel, "assistant", response_text)
        
        return {
            "response": response_text,
            "notify_admin": consultation_trigger,
            "user_id": user_id
        }
    except Exception as e:
        print(f"⚠️ Chat Error v11.1: {e}")
        return {"response": "Javi, error de enlace en el hilo multinodal. Reintentando...", "notify_admin": False}

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
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_frame:
                frame_path = tmp_frame.name
                cv2.imwrite(frame_path, frame)
                frames.append(frame_path)
    cap.release()
    return frames

def optimizar_imagen(file_path):
    import PIL.Image
    path_orig = Path(file_path)
    if not path_orig.exists(): return file_path
    
    # Saneamiento v11.1: Siempre optimizar para asegurar bajo consumo de RAM en Render
    print(f"⚡ Optimizando imagen (1024px max) para ahorro de RAM...")
    try:
        img = PIL.Image.open(file_path)
        # Convertir a RGB si es necesario (evitar errores con RGBA en JPEG)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        img.thumbnail((1024, 1024), PIL.Image.Resampling.LANCZOS)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_opt:
            opt_path = tmp_opt.name
            img.save(opt_path, "JPEG", quality=70, optimize=True)
        img.close()
        return opt_path
    except Exception as e:
        print(f"⚠️ Fallo al optimizar imagen: {e}")
        return file_path

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

        # Intento 1: GROQ VISION (Prioridad v11.1 - 90b)
        print("👁️ Nora intentando Groq Vision (90b)...")
        p_main = paths[0] 
        p_opt = optimizar_imagen(p_main)
        if p_opt != str(p_main): temporales.append(p_opt)
                
        base64_image = encode_image(p_opt)
        
        # Saneamiento v11.1: Lista de modelos a probar en orden
        modelos_a_probar = [
            "llama-3.2-90b-vision-preview",
            "llama-3.2-11b-vision-preview-free", # Fallback por si lo reactivan
            "meta-llama/llama-4-scout-17b-16e-instruct" # Plan C (Siguiente generación)
        ]
                
        for model_id in modelos_a_probar:
            try:
                print(f"🔄 Probando modelo: {model_id}...")
                completion = groq_client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "user", "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]}
                    ],
                    temperature=0.1,
                    max_tokens=1024
                )
                res = completion.choices[0].message.content
                if not res or not res.strip():
                    print(f"⚠️ El modelo {model_id} devolvió una respuesta vacía. Pasando al siguiente.")
                    continue
                    
                body = res.strip()
                m_used = model_id
                done = True
                print(f"✅ Análisis de visión completado con éxito ({m_used}).")
                break
            except Exception as e:
                if "decommissioned" in str(e).lower():
                    continue
                err_str = str(e).lower()
                if "400" in err_str and "decommissioned" in err_str:
                    print(f"⚠️ MODELO DECOMISIONADO: {model_id}. Pasando al siguiente.")
                elif "404" in err_str or "not found" in err_str:
                    print(f"⚠️ MODELO NO ENCONTRADO: {model_id}. Pasando al siguiente.")
                else:
                    print(f"⚠️ Error con {model_id}: {e}")
                    if model_id == modelos_a_probar[-1]: # Si es el último, lanzar la excepción
                        raise e

    except Exception as e:
        err_msg = f"❌ DEBUG VISION - Error total tras agotar modelos: {str(e)}"
        print(err_msg)
        traceback.print_exc()
        body = "Javi, veo la imagen pero no puedo describirla con claridad ahora mismo."
        done = True

        # Fallback a Gemini si Groq falla
        if not done and gemini_model:
            print("👁️ Intentando Fallback a Gemini (v11.1 Ready)...")
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
                        ia_local_store.registrar_operacion_contable(user_id=user_id, monto=float(data.get("total")), proveedor=data.get("emisor"), concepto="Groq Vision v11.1")
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
    print("🧠 Nora Brain v11.1 (Render Cloud) Online.")
