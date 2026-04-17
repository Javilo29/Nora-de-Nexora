# Proyecto: Nora de Nexora - MyJNexoraVisual (v5.9.5)
import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
# 1) Raíz del repositorio (válida aunque el cwd sea Guiones u otra carpeta)
load_dotenv(dotenv_path=str(ENV_FILE), override=True)
# 2) find_dotenv: búsqueda desde cwd hacia arriba (complemento sin pisar claves ya cargadas)
_alt = find_dotenv()
if _alt and Path(_alt).resolve() != ENV_FILE.resolve():
    load_dotenv(dotenv_path=_alt, override=False)

# Base de Datos SQLite (Soberanía Disco D)
LOCAL_DB_FILE = BASE_DIR / "datos" / "db" / "nexora_multirrubro.sqlite"
LOCAL_DB_ROOT = BASE_DIR / "datos" / "Base_Datos"
LOCAL_DB_ROOT.mkdir(parents=True, exist_ok=True)

SCRIPTS_DIR = BASE_DIR / "Guiones"
KNOWLEDGE_DIR = BASE_DIR / "Conocimiento"
ASSETS_DIR = BASE_DIR / "Assets"
REPORT_DIR = BASE_DIR / "Reportes"
INBOX_DIR = BASE_DIR / "Inbox"
LOGS_DIR = BASE_DIR / "LOGS"
SECURITY_LOGS_DIR = LOGS_DIR / "Seguridad"
VISION_HISTORY_DIR = BASE_DIR / "datos" / "vision_history"
VISION_HISTORY_LOG = LOGS_DIR / "vision_history.txt"
# Biometría (solo Gemini API + OpenCV opcional; sin librería DeepFace en disco)
BIOMETRIA_ROOT = BASE_DIR / "Biometria"
BIOMETRIA_JAVIER_DIR = BIOMETRIA_ROOT / "Assets" / "Biometria" / "Javier"
TMP_DIR = BASE_DIR / "tmp"

DATA_DIR = BASE_DIR / "datos"
DB_DIR = DATA_DIR / "db"
VAULT_DIR = DATA_DIR / "vault"


def ensure_structure():
    """Asegura que todas las carpetas necesarias existan en el BASE_DIR."""
    directories = [
        KNOWLEDGE_DIR,
        ASSETS_DIR,
        REPORT_DIR,
        INBOX_DIR,
        LOGS_DIR,
        SECURITY_LOGS_DIR,
        BIOMETRIA_ROOT,
        BIOMETRIA_JAVIER_DIR,
        TMP_DIR,
        DB_DIR,
        VAULT_DIR,
        LOCAL_DB_ROOT,
        VISION_HISTORY_DIR,
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    print(f"🚀 Nora BASE_DIR (Soberanía D:): {BASE_DIR}")
    ensure_structure()
    print(f"📂 DB SQLite: {LOCAL_DB_FILE}")
    print("✅ Estructura de carpetas verificada.")
