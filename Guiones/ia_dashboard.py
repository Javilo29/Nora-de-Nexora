# -*- coding: utf-8 -*-
# Nexora Pro — Panel ejecutivo v5.9.5 (consultoría multirrubro)
import os
import sys
from pathlib import Path

GUI = Path(__file__).resolve().parent
if str(GUI) not in sys.path:
    sys.path.insert(0, str(GUI))

import ia_paths  # noqa: F401 — carga load_dotenv(find_dotenv())

from ia_paths import BASE_DIR

BASE = BASE_DIR

import pandas as pd
import streamlit as st

import ia_local_store
from ia_local_store import METADATA_ENTITY_LABEL, METADATA_UNIT_LABEL

st.set_page_config(
    page_title="Nexora Pro v8.2 — Panel Multinodal",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def _db_files():
    roots = [
        BASE / "data" / "db",
        BASE / "data" / "Base_Datos",
    ]
    out = []
    for r in roots:
        if r.is_dir():
            out.extend(r.glob("*.db"))
    return sorted(set(out))


@st.cache_data(ttl=30)
def _channel_status():
    return {
        "telegram": bool((os.getenv("TELEGRAM_TOKEN") or "").strip()),
        "whatsapp": bool((os.getenv("WHATSAPP_TOKEN") or "").strip()),
        "admin_id": bool((os.getenv("TELEGRAM_ADMIN_ID") or "").strip()),
        "groq": bool((os.getenv("GROQ_API_KEY") or "").strip()),
        "work_mode": (os.getenv("WORK_MODE") or "Multinodal v8.2").strip(),
    }


@st.cache_data(ttl=15)
def _multirrubro_metrics():
    ia_local_store.seed_demo_if_empty()
    return ia_local_store.operational_metrics()


@st.cache_data(ttl=15)
def _embudo_consultoria():
    ia_local_store.seed_demo_if_empty()
    return ia_local_store.embudo_consultoria_metrics()


def _total_db_kb(paths: list) -> float:
    return sum(p.stat().st_size for p in paths) / 1024.0 if paths else 0.0


def _holding_health_index(ch: dict, mm: dict, dbs: list) -> tuple[int, list[tuple[str, str, int]]]:
    """Índice 0–100 y desglose cualitativo para la vista de director."""
    score = 0
    parts: list[tuple[str, str, int]] = []
    if ch["telegram"]:
        score += 24
        parts.append(("Canal Telegram", "Operativo", 24))
    else:
        parts.append(("Canal Telegram", "Pendiente", 0))
    if ch["admin_id"]:
        score += 22
        parts.append(("Admin Telegram", "Definido", 22))
    else:
        parts.append(("Admin Telegram", "Pendiente", 0))
    if ch["groq"]:
        score += 30
        parts.append(("Motor IA (Groq 70B)", "Listo", 30))
    else:
        parts.append(("Motor IA (Groq 70B)", "Pendiente", 0))
    if mm["total_unidades_negocio"] > 0:
        score += 12
        parts.append(("Unidades de negocio (datos)", "Registradas", 12))
    else:
        parts.append(("Unidades de negocio (datos)", "Vacío", 0))
    if mm["total_clientes_contactos"] > 0:
        score += 12
        parts.append(("Clientes / contactos", "Registrados", 12))
    else:
        parts.append(("Clientes / contactos", "Vacío", 0))
    kb = _total_db_kb(dbs)
    if kb > 0:
        bonus = min(8, int(kb / 500))
        score += bonus
        parts.append(("Persistencia local (.db)", f"~{kb:.0f} KB", bonus))
    return min(100, score), parts


def main():
    st.title("Nexora Pro v8.2 — Multinode & Business Gateway")
    st.caption(f"Infraestructura de Holding · Proyecto: `{BASE}`")

    ch = _channel_status()
    dbs = _db_files()
    mm = _multirrubro_metrics()
    emb = _embudo_consultoria()
    health, health_parts = _holding_health_index(ch, mm, dbs)

    st.subheader("Salud del Holding")
    st.caption(
        "Vista ejecutiva: integraciones críticas, motor 70B y base multirrubro. "
        "Un índice alto indica menor riesgo operativo al escalar líneas de ingreso."
    )
    h1, h2 = st.columns([1, 2])
    with h1:
        st.metric("Índice de salud del Holding", f"{health} / 100")
        st.progress(min(1.0, health / 100.0))
        if health >= 85:
            st.success("Perfil sólido para decisión de director.")
        elif health >= 55:
            st.warning("Operativo con brechas; revise canales o datos multirrubro.")
        else:
            st.error("Riesgo elevado: complete .env y datos mínimos antes de producción.")
    with h2:
        hp = pd.DataFrame(health_parts, columns=["Componente", "Estado", "Peso"])
        hp_chart = hp.set_index("Componente")["Peso"]
        if hp_chart.sum() > 0:
            st.bar_chart(hp_chart)
        else:
            st.info("Sin pesos asignados hasta configurar integraciones.")

    st.subheader("Estado de Canales y Gateway")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.success("Telegram OK") if ch["telegram"] else st.warning("Telegram Offline")
    with c2:
        st.success("WhatsApp OK") if ch["whatsapp"] else st.warning("WhatsApp Offline")
    with c3:
        st.success("Groq Motor (70B) LListo") if ch["groq"] else st.warning("Groq Offline")
    with c4:
        st.metric("Modo operativo", ch["work_mode"])

    st.subheader("Monitoreo de Prospectos (v8.2 Business Gateway)")
    st.caption("Leads activos extraídos de WhatsApp y Telegram. Clasificación por interés y estado del embudo.")
    prospects = ia_local_store.get_prospects_summary()
    if prospects:
        df_p = pd.DataFrame(prospects)
        st.dataframe(df_p, use_container_width=True, hide_index=True)
    else:
        st.info("No hay prospectos registrados en el ciclo actual.")

    st.subheader("Embudo de Consultoría")
    st.caption(
        "Leads en **gestion_consultoria**: de primer contacto y saneamiento de dudas hasta "
        "listo para cierre humano y acuerdo firmado."
    )
    df_emb = pd.DataFrame(emb["por_fase"])
    if emb["total_prospectos"] > 0:
        st.dataframe(df_emb, hide_index=True)
        chart_e = df_emb.set_index("fase")[["prospectos"]]
        st.bar_chart(chart_e)
    else:
        st.info("Sin prospectos en el embudo. Use `ia_local_store.registrar_prospecto_consultoria` o ejecute la simulación.")
    st.metric("Total prospectos en embudo", emb["total_prospectos"])

    st.subheader("Métricas multirrubro v5.9.5")
    st.caption(
        "Por **Unidad de Negocio** y **Clientes/Contactos**: base para interpretar ingresos por línea, "
        "sector o proyecto sin atarse a un solo rubro."
    )
    st.text(f"Almacén: {mm['db_path']}")
    m1, m2 = st.columns(2)
    with m1:
        st.metric("Unidades de negocio", mm["total_unidades_negocio"])
    with m2:
        st.metric("Clientes / contactos", mm["total_clientes_contactos"])
    if mm["desglose_por_unidad"]:
        st.dataframe(mm["desglose_por_unidad"], hide_index=True)
        dfu = pd.DataFrame(mm["desglose_por_unidad"])
        if METADATA_UNIT_LABEL in dfu.columns and METADATA_ENTITY_LABEL in dfu.columns:
            chart = dfu.set_index(METADATA_UNIT_LABEL)[[METADATA_ENTITY_LABEL]]
            st.caption("Distribución de **Clientes/Contactos** por **Unidad de Negocio** (proxy de carga por línea).")
            st.bar_chart(chart)
    else:
        st.info("Sin unidades registradas. Use `ia_local_store` o integraciones para poblar datos.")

    st.subheader("Bases de datos locales (*.db)")
    if dbs:
        st.dataframe(
            [{"archivo": str(p.relative_to(BASE)), "tamaño_kb": round(p.stat().st_size / 1024, 1)} for p in dbs],
            hide_index=True,
        )
        st.caption("Útil para auditoría, Telegram u otros flujos; el tamaño agregado sirve como proxy de actividad.")
    else:
        st.info(
            "No se encontraron `.db` adicionales en `data/db` ni `data/Base_Datos`. "
            "La métrica multirrubro usa `data/Base_Datos/nexora_multirrubro.sqlite`."
        )

    st.subheader("Rutas")
    st.code(
        f"BASE_DIR = {BASE}\n"
        f"Guiones = {GUI}\n"
        f"Conocimiento = {BASE / 'Conocimiento'}\n"
        f"LOCAL_DB_ROOT = {ia_paths.LOCAL_DB_ROOT}",
        language="text",
    )


def _inside_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        return get_script_run_ctx() is not None
    except Exception:
        return False


if __name__ == "__main__":
    if _inside_streamlit():
        main()
    else:
        from streamlit.web import bootstrap

        bootstrap.run(str(Path(__file__).resolve()), False, [], {})
