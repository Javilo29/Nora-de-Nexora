# -*- coding: utf-8 -*-
"""Prueba de versatilidad v5.2 — consultoría técnica (no solo rubro salud)."""
import sys
from pathlib import Path

_G = Path(__file__).resolve().parent
if str(_G) not in sys.path:
    sys.path.insert(0, str(_G))

import ia_brain  # noqa: E402

PROMPT = (
    "En su rol de Directora de Operaciones Diversificadas (v5.9.5), describa en 4–6 frases "
    "cómo estructuraría el arranque de un nuevo departamento de consultoría técnica en "
    "MyJNexoraVisual: gobierno, KPIs, agenda y vínculo con contabilidad. Trato de usted."
)


def main():
    if not ia_brain.groq_client and not ia_brain.gemini_model:
        print("Sin motor de IA (Groq/Gemini). Revise .env.")
        sys.exit(1)
    out = ia_brain.chat_with_nora(PROMPT)
    print(out)
    if "[Nora de Nexora v5.9.5]" not in out:
        sys.exit(2)


if __name__ == "__main__":
    main()
