# Proyecto: Nora de Nexora - MyJNexoraVisual
import streamlit as st
import pandas as pd
import os
import time
from dotenv import load_dotenv, set_key
from ia_paths import BASE_DIR, ENV_FILE, REPORT_DIR, ASSETS_DIR

# Estética Premium: Nexora Visual
st.set_page_config(page_title="Nora de Nexora - MyJNexoraVisual", page_icon="🧠", layout="wide")

# Carga de Configuración (Ruta Dinámica)
load_dotenv(str(ENV_FILE))

def save_config(gemini_key, supabase_url, mode):
    set_key(str(ENV_FILE), "GEMINI_API_KEY", gemini_key)
    set_key(str(ENV_FILE), "SUPABASE_URL", supabase_url)
    set_key(str(ENV_FILE), "WORK_MODE", mode)
    st.success("Configuración Guardada. Nora está lista para reiniciar.")

st.title("🧠 Nora de Nexora")
st.subheader("Soy Nora de Nexora. Bienvenida/o a la central de MyJNexoraVisual.")
st.write("Estoy lista para auditar tus cuentas y guiar tu aprendizaje.")

tab1, tab2, tab3 = st.tabs(["⚙️ Configuración", "📊 Dashboard", "📟 Consola"])

with tab1:
    st.header("Ajustes del Sistema")
    gemini_key = st.text_input("Gemini API Key", value=os.environ.get("GEMINI_API_KEY", ""), type="password")
    supabase_url = st.text_input("Supabase URL", value=os.environ.get("SUPABASE_URL", ""))
    mode = st.selectbox("Modo de Trabajo", ["Contabilidad", "Educativo"], index=0 if os.environ.get("WORK_MODE")=="Contabilidad" else 1)
    
    if st.button("Guardar Cambios"):
        save_config(gemini_key, supabase_url, mode)

with tab2:
    st.header("Seguimiento de Documentos")
    # Simulación de datos
    data = {"Documento": ["Factura_Almia.txt", "Recibo_Julio.pdf", "Nota_Credito.jpg"],
            "Estado": ["🔴 RECHAZADO_NO_FISCAL", "🟢 Verificado", "🟡 Error_Calculo"],
            "Fecha": ["2026-03-29", "2026-03-28", "2026-03-28"]}
    df = pd.DataFrame(data)
    st.table(df)
    
    if st.button("Generar Reporte Detallado"):
        st.info(f"Generando reporte en {REPORT_DIR}...")
        time.sleep(1)
        st.success("Reporte generado con éxito.")

with tab3:
    st.header("Monitor en Tiempo Real")
    st.code(">>> Nora Inicializada\n>>> Escaneando Inbox...\n>>> Nora está escuchando...", language="python")
    
    st.divider()
    st.subheader("🌐 Nora Link (Telegram)")
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    user_id = os.environ.get("TELEGRAM_USER_ID")
    
    if token and user_id:
        st.success("Acceso Remoto Configurado: Bot Listo.")
        if st.button("🚀 Iniciar Nora Link"):
            import subprocess
            subprocess.Popen(["python", str(BASE_DIR / "Scripts" / "ia_telegram_bot.py")])
            st.info("Nora Link se está ejecutando en segundo plano.")
    else:
        st.warning("Acceso Remoto Deshabilitado. Configura el Token en .env.")

avatar_path = ASSETS_DIR / "nora_avatar_premium.png"
if avatar_path.exists():
    st.sidebar.image(str(avatar_path), width=200)
else:
    st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRz-k5f0_O7m8u7M0p_8j9X1yX2_7Q4-S4w_A&s", width=200)

st.sidebar.markdown("---")
st.sidebar.info("Nora de Nexora v1.0\nMyJNexoraVisual")
