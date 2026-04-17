# Proyecto: Nora de Nexora - MyJNexoraVisual
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from ia_paths import REPORT_DIR, ENV_FILE

load_dotenv(dotenv_path=str(ENV_FILE))

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SUPABASE_CLIENT: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY and "tu-proyecto" not in SUPABASE_URL else None

REPORTS_PATH = REPORT_DIR

def generate_professional_alert(cliente_id, client_name, doc_name, amount):
    """Genera un reporte ejecutivo para alertas no-fiscales."""
    if not os.path.exists(REPORTS_PATH):
        os.makedirs(REPORTS_PATH)

    print(f"🖋️ Nora redactando alerta profesional para {client_name}...")
    
    report_file = os.path.join(REPORTS_PATH, f"Alerta_No_Fiscal_{cliente_id}.txt")
    
    content = f"""ATENCIÓN PROFESIONAL: VALIDACIÓN TÉCNICA

Sujeto: Alerta de Comprobante No-Fiscal
Cliente: {client_name} (ID: {cliente_id})
Documento: {doc_name}
Monto: ${amount}

ANÁLISIS DE NORA:
El documento cargado por el cliente es un COMPROBANTE INTERNO.
Carece de CUIT del emisor y CAE (autorización fiscal).

RECOMENDACIÓN:
Se recomienda al profesional contable solicitar al cliente la Factura A o B legal 
y advertir sobre los riesgos de registrar gastos sin comprobantes autorizados.

Fecha del reporte: {os.popen('date /t').read().strip()}
"""
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"✨ Alerta profesional guardada en: {report_file}")

if __name__ == "__main__":
    # Generamos el reporte para el caso Almia Clothes como ejemplo solicitado
    generate_professional_alert(
        cliente_id="CLIENT-001",
        client_name="Maria Itati Palacio",
        doc_name="Comprobante Almia Clothes",
        amount="14.500,00"
    )
