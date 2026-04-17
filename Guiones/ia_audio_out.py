# -*- coding: utf-8 -*-
# Nora v5.6 — salida de voz (altavoz local o reproducción de archivo generado)
import os
import sys
import tempfile
import subprocess
from pathlib import Path

GREETING_JAVIER_DEFAULT = (
    "Buenos días, Javier. Estoy lista para comenzar. ¿Qué tenemos en agenda hoy?"
)


def speak(text: str, prefer: str = "auto") -> bool:
    """
    Emite texto por altavoz.
    prefer: 'pyttsx3' (offline, síncrono), 'gtts' (Google TTS + reproducción), 'auto' (prueba pyttsx3 y luego gTTS).
    """
    text = (text or "").strip()
    if not text:
        return False

    if prefer in ("auto", "pyttsx3"):
        try:
            import pyttsx3

            engine = pyttsx3.init()
            try:
                rate = int(os.environ.get("NORA_TTS_RATE", "175"))
                engine.setProperty("rate", rate)
            except Exception:
                pass
            engine.say(text)
            engine.runAndWait()
            return True
        except Exception:
            if prefer == "pyttsx3":
                return False

    if prefer in ("auto", "gtts"):
        try:
            from gtts import gTTS

            tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            tmp.close()
            path = Path(tmp.name)
            tts = gTTS(text=text, lang="es", slow=False)
            tts.save(str(path))
            if sys.platform == "win32":
                os.startfile(str(path))  # noqa: S606
            elif sys.platform == "darwin":
                subprocess.run(["open", str(path)], check=False)
            else:
                subprocess.run(["xdg-open", str(path)], check=False)
            return True
        except Exception:
            try:
                path.unlink(missing_ok=True)
            except Exception:
                pass
            return False
    return False
