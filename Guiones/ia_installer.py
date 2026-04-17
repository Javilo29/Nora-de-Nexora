import os
import shutil

# Configuración del Instalador
INSTALL_DIR = r"D:\NORA_AI"
SOURCE_DIR = r"D:\AGENTE_IA"

def create_structure():
    print(f"🚀 Iniciando Instalación de Nora AI en {INSTALL_DIR}...")
    
    folders = [
        os.path.join(INSTALL_DIR, "data", "db"),
        os.path.join(INSTALL_DIR, "data", "vault", "inbound"),
        os.path.join(INSTALL_DIR, "Knowledge"),
        os.path.join(INSTALL_DIR, "Scripts"),
        os.path.join(INSTALL_DIR, "Reportes"),
        os.path.join(INSTALL_DIR, "LOGS"),
        os.path.join(INSTALL_DIR, "tmp")
    ]
    
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"✅ Carpeta creada: {folder}")

def deploy_base_files():
    print("📦 Desplegando archivos base...")
    # Archivos críticos para copiar (Simulamos copia de scripts existentes)
    scripts = ["ia_brain.py", "ia_responder.py", "ia_app.py", "ia_professional_report.py"]
    for script in scripts:
        src = os.path.join(SOURCE_DIR, "Scripts", script)
        dst = os.path.join(INSTALL_DIR, "Scripts", script)
        if os.path.exists(src):
            shutil.copy(src, dst)
            print(f"✅ Copiado: {script}")

    knowledge = "pedagogia_contable.json"
    src_k = os.path.join(SOURCE_DIR, "Knowledge", knowledge)
    dst_k = os.path.join(INSTALL_DIR, "Knowledge", knowledge)
    if os.path.exists(src_k):
        shutil.copy(src_k, dst_k)

def generate_initial_env():
    env_file = os.path.join(INSTALL_DIR, ".env")
    if not os.path.exists(env_file):
        with open(env_file, "w") as f:
            f.write("# Nora AI - Archivo de Configuración Inicial\n")
            f.write("GEMINI_API_KEY=PEGUE_AQUI_SU_KEY\n")
            f.write("SUPABASE_URL=URL_PROYECTO\n")
            f.write("WORK_MODE=Contabilidad\n")
        print(f"✅ Archivo .env inicial creado en {INSTALL_DIR}")

if __name__ == "__main__":
    create_structure()
    deploy_base_files()
    generate_initial_env()
    print("\n🎉 Instalación completada. Nora AI está lista para ser configurada.")
