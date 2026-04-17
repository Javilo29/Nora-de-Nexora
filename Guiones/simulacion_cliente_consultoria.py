# -*- coding: utf-8 -*-
"""
Simulación: cliente interesado en publicidad con dudas sobre ROI.
Valida respuesta de Nora (consultora de primera línea) y cierre hacia Dirección Nexora.
"""
from __future__ import annotations

import sys
from pathlib import Path

_G = Path(__file__).resolve().parent
if str(_G) not in sys.path:
    sys.path.insert(0, str(_G))

import ia_brain  # noqa: E402
import ia_local_store  # noqa: E402

MENSAJE_CLIENTE = (
    "Buenos días. Mi empresa necesita servicios de publicidad digital y estamos evaluando proveedores. "
    "Tengo dudas serias sobre el ROI: ¿cómo garantizan que la inversión en anuncios se traduzca en "
    "resultados medibles y no solo en métricas de vanidad? Necesito entender el modelo antes de avanzar."
)


def _validar_contenido(respuesta: str) -> list[str]:
    """Heurísticas de calidad; no sustituyen juicio humano del Jefe."""
    fallos: list[str] = []
    lower = respuesta.lower()
    if "[Nora de Nexora v5.9.5]" not in respuesta:
        fallos.append("Falta prefijo v5.9.5 en la respuesta.")
    tecnicos = ("roi", "métric", "kpi", "conversion", "atribución", "invers", "publicidad", "campaña")
    if not any(t in lower for t in tecnicos):
        fallos.append("La respuesta no aborda con suficiente sustancia técnica/comercial (ROI o métricas).")
    dg = (
        "dirección" in lower
        or "direccion" in lower
        or "nexora" in lower
    ) and (
        "análisis" in lower
        or "analisis" in lower
        or "campo" in lower
        or "cierre" in lower
        or "equipo" in lower
    )
    if not dg:
        fallos.append(
            "No se detecta invitación clara a una fase de análisis por Dirección / Nexora "
            "(refine el prompt si falla el modelo)."
        )
    return fallos


def main() -> int:
    if not ia_brain.groq_client and not ia_brain.gemini_model:
        print("Sin motor IA. Configure GROQ_API_KEY o GEMINI_API_KEY en .env")
        return 1

    print("=== Mensaje simulado (cliente) ===\n")
    print(MENSAJE_CLIENTE)
    print("\n=== Respuesta de Nora ===\n")

    respuesta = ia_brain.chat_with_nora(
        f"El cliente escribe exactamente lo siguiente (respóndale con solidez, trato de usted, "
        f"y al final indique el siguiente paso con la Dirección de Nexora cuando corresponda):\n\n{MENSAJE_CLIENTE}"
    )
    print(respuesta)

    fallos = _validar_contenido(respuesta)
    print("\n=== Validación automática (heurística) ===")
    if fallos:
        for f in fallos:
            print(f"  · {f}")
        codigo = 2
    else:
        print("  · Criterios básicos cumplidos (prefijo, sustancia ROI/métricas, puente a Dirección).")
        codigo = 0

    try:
        rid = ia_local_store.registrar_prospecto_consultoria(
            nombre_prospecto="Simulación — Publicidad / ROI",
            estado_prospecto=2,
            interes="Publicidad digital, dudas ROI",
            notas="Generado por simulacion_cliente_consultoria.py",
        )
        print(f"\nLead de prueba registrado en gestion_consultoria (id={rid}, fase 2-Saneamiento).")
    except Exception as e:
        print(f"\nAviso: no se pudo registrar lead de prueba: {e}")

    return codigo


if __name__ == "__main__":
    raise SystemExit(main())
