# Proyecto: Nora de Nexora - MyJNexoraVisual
import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv
from ia_paths import REPORT_DIR, ENV_FILE

load_dotenv(dotenv_path=str(ENV_FILE))

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SUPABASE_CLIENT: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY and "tu-proyecto" not in SUPABASE_URL else None

# REPORTS_PATH dinámico desde ia_paths
REPORTS_PATH = REPORT_DIR

def ensure_reports_dir():
    if not os.path.exists(REPORTS_PATH):
        os.makedirs(REPORTS_PATH)

def generate_pending_summary(cliente_id):
    """Agrupa documentos pendientes de verificación y genera un reporte rápido."""
    if not SUPABASE_CLIENT:
        print("❌ Error: No hay conexión con la nube para generar el resumen.")
        return

    print(f"📊 Generando resumen técnico para el Contador (Cliente: {cliente_id})...")
    
    try:
        # Filtro de seguridad (ia_)
        res = SUPABASE_CLIENT.table("ia_documentos")\
            .select("*")\
            .eq("cliente_id", cliente_id)\
            .in_("estado", ["Pendiente_Verificacion", "Error_Calculo"])\
            .execute()
        
        docs = res.data
        if not docs:
            print("✅ No hay documentos pendientes para este cliente.")
            return

        ensure_reports_dir()
        report_file = os.path.join(REPORTS_PATH, f"Resumen_Contador_{cliente_id}.txt")
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(f"REPORTE TÉCNICO DE NORA - CLIENTE ID: {cliente_id}\n")
            f.write("="*50 + "\n\n")
            
            for doc in docs:
                f.write(f"Documento: {doc.get('url_storage', 'N/A')}\n")
                f.write(f"Estado: {doc.get('estado')}\n")
                f.write(f"Tipo Detectado: {doc.get('tipo', 'Desconocido')}\n")
                if doc.get('estado') == "Error_Calculo":
                    f.write("ALERTA: Discordancia entre Neto+IVA y Total.\n")
                f.write("-" * 30 + "\n")
        
        print(f"✨ Reporte generado con éxito en: {report_file}")
        
    except Exception as e:
        print(f"❌ Error al generar reporte: {e}")

if __name__ == "__main__":
    # Prueba mock
    generate_pending_summary("TEST_UUID")
