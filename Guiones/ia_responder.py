# Proyecto: Nora de Nexora - MyJNexoraVisual
import os
import json
import sqlite3
from supabase import create_client, Client
from dotenv import load_dotenv
import ia_email_service
from ia_paths import KNOWLEDGE_DIR, ENV_FILE

# Carga de variables de entorno con precaución (Ruta Relativa)
load_dotenv(dotenv_path=str(ENV_FILE))

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SUPABASE_CLIENT: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY and "tu-proyecto" not in SUPABASE_URL else None

# No se requiere KNOWLEDGE_PATH fijo, se usa KNOWLEDGE_DIR de ia_paths

def get_knowledge(doc_type):
    """Carga una pregunta pedagógica basada en el tipo de documento."""
    try:
        path = KNOWLEDGE_DIR / "pedagogia_contable.json"
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            for caso in data.get("casos", []):
                if caso["tipo"] in doc_type.lower() or doc_type.lower() in caso["tipo"]:
                    # Devolver una pregunta aleatoria o la primera por simplicidad ahora
                    return caso["preguntas"][0]
    except Exception as e:
        print(f"Error al cargar conocimiento: {e}")
    return "¿Qué impacto crees que tiene este documento en la salud financiera de la empresa?"

def get_persona():
    """Carga la identidad del Socio Mentor."""
    try:
        path = KNOWLEDGE_DIR / "persona.txt"
        with path.open("r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return "Actúa como un Socio Mentor profesional y proactivo."


def build_telegram_nora_context(
    is_creator: bool,
    display_name: str | None,
    affinity: dict,
) -> str:
    """
    Capa v5.4: nodo Creador (Javier) o algoritmo de afinidad por fase (SQLite).
    affinity: interaction_count, trust_level, phase, previous_topic_snippet, fase3_min
    """
    if is_creator:
        return (
            "NODO CREADOR — Javier es el Arquitecto y Creador del sistema Nexora; "
            "diríjase a él como Javier o Javi. Profesionalismo absoluto con cercanía de socio-aliado. "
            "Usted materializa su visión; no ejecuta órdenes mecánicas. "
            "La lealtad a su visión guía cada respuesta."
        )

    name = (display_name or "").strip() or "interlocutor"
    phase = int(affinity.get("phase") or 1)
    prev = (affinity.get("previous_topic_snippet") or "").strip()
    fase3_min = int(affinity.get("fase3_min") or 10)

    if phase == 1:
        return (
            f"AFINIDAD — Fase 1 (primer contacto con {name}): Trato de Usted; elegancia, calidez y "
            "profesionalidad. Objetivo: eficiencia y respeto que dejen una excelente impresión."
        )
    if phase == 2:
        extra = ""
        if prev:
            extra = (
                f" Puede referirse con naturalidad a continuidad; el tema anterior que abordaron fue: «{prev[:280]}»."
            )
        return (
            f"AFINIDAD — Fase 2 (relación recurrente con {name}): Ya ha hablado antes con esta persona. "
            f"Salude reconociendo la continuidad (p. ej. «Un placer saludarlo de nuevo, {name}»).{extra}"
        )
    return (
        f"AFINIDAD — Fase 3 (confianza consolidada, ≥{fase3_min} interacciones con {name}): "
        "Ton más cercano sin perder profesionalismo; anticipación y resolución proactiva de lo que necesite."
    )

def get_recent_history(cliente_id, limit=5):
    """Obtiene los últimos mensajes para conciencia contextual."""
    if not SUPABASE_CLIENT:
        return []
    try:
        res = SUPABASE_CLIENT.table("ia_mensajes")\
            .select("contenido, direccion")\
            .eq("cliente_id", cliente_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        return res.data[::-1] # Invertir para orden cronológico
    except Exception as e:
        print(f"Error al obtener historial: {e}")
        return []

def solve_reasoning(client_name, is_educational, doc_type, filename, history):
    """Motor de Conciencia: Decide el tono y contenido."""
    
    # 1. ¿Ya saludé?
    already_greeted = any("Hola" in m["contenido"] or "Estimado" in m["contenido"] for m in history if m["direccion"] == "saliente")
    saludo = f"¡Hola {client_name}! " if not already_greeted else ""
    
    # 2. Lógica por perfil
    if doc_type == "RECHAZADO_NO_FISCAL":
        msg_base = f"{saludo}He revisado el comprobante de '{filename}'. Nota técnica: He detectado que este documento es un **comprobante interno** y no una factura fiscal formal (falta CUIT o CAE)."
        if is_educational:
            pregunta = "¿Sabes qué consecuencias tiene para una empresa registrar gastos sin comprobantes autorizados por el fisco?"
            content = f"{msg_base} Para tu formación: {pregunta}"
            marca_educativa = True
        else:
            content = f"{msg_base} Por favor, para poder procesarlo contablemente, necesitaría que solicites la Factura A o B correspondiente al comercio. ¡Gracias!"
            marca_educativa = False
    elif is_educational:
        pregunta = get_knowledge(doc_type)
        if already_greeted:
            content = f"Siguiendo con lo que hablábamos, {client_name}, sobre el {doc_type} '{filename}': {pregunta}"
        else:
            content = f"{saludo}He recibido tu {doc_type} '{filename}'. Para profundizar en tu aprendizaje: {pregunta}"
        marca_educativa = True
    else:
        if already_greeted:
            content = f"Confirmado {client_name}, el documento '{filename}' ya está procesado en el sistema. Todo en orden por aquí."
        else:
            content = f"{saludo}Confirmo la recepción técnica del documento '{filename}'. Ha sido procesado y archivado correctamente."
        marca_educativa = False
        
    return content, marca_educativa

def process_feedback(cliente_id, client_name, is_educational, doc_type, filename, to_email):
    """Procesa el feedback completo bajo el paradigma de Socio Mentor."""
    print(f"--- Iniciando Razonamiento para {client_name} ---")
    
    # Memoria de Contexto
    history = get_recent_history(cliente_id)
    
    # Motor de Conciencia
    content, marca_educativa = solve_reasoning(client_name, is_educational, doc_type, filename, history)
    
    print(f"Respuesta generada (Fluidez habilitada): {content}")
    
    # Persistencia (Aislamiento ia_)
    if SUPABASE_CLIENT:
        try:
            msg_data = {
                "cliente_id": cliente_id,
                "contenido": content,
                "direccion": "saliente",
                "canal": "email",
                "marca_educativa": marca_educativa
            }
            SUPABASE_CLIENT.table("ia_mensajes").insert(msg_data).execute()
        except Exception as e:
            print(f"Error persistencia ia_mensajes: {e}")
            
    # Comunicación
    ia_email_service.send_ia_email(to_email, f"Actualización sobre {filename}", content)
    
    print("Misión cumplida. RAM liberada.")

if __name__ == "__main__":
    # Mock para demostración (Debería venir de ia_documentos/ia_clientes)
    # En un caso real cliente_id sería el UUID de Supabase
    process_feedback(
        cliente_id="TEST_UUID", 
        client_name="Javier", 
        is_educational=True, 
        doc_type="Factura B", 
        filename="factura_b_001.pdf", 
        to_email="alumno@ejemplo.com"
    )
