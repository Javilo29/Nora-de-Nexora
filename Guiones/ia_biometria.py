# -*- coding: utf-8 -*-
"""
Nora Light (v5.9.5) — Visión sin modelos pesados: movimiento OpenCV + reconocimiento Gemini 1.5 API.
Sin TensorFlow/Keras/DeepFace: solo opencv (opcional) + google-generativeai.

Requiere fotos de referencia en Biometria/Assets/Biometria/Javier y GEMINI_API_KEY en .env.

Variables: NORA_CAMERA_INDEX, NORA_CAMERA_URL, NORA_GEMINI_CONFIDENCE_MIN (85),
NORA_MOTION_THRESHOLD, NORA_MOTION_MIN_AREA, NORA_MIN_SECONDS_BETWEEN_API,
SENTINEL_HORA_INICIO, SENTINEL_HORA_FIN, NORA_JAVIER_COOLDOWN_SEC, NORA_SENTINEL_COOLDOWN_SEC
"""
from __future__ import annotations

import logging
import os
import shutil
import time
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("NoraBiometria")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")


def _paths():
    from ia_paths import BIOMETRIA_JAVIER_DIR, SECURITY_LOGS_DIR, TMP_DIR, ensure_structure

    ensure_structure()
    return BIOMETRIA_JAVIER_DIR, SECURITY_LOGS_DIR, TMP_DIR


def _list_ref_images(bdir: Path) -> list[Path]:
    exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    if not bdir.is_dir():
        return []
    return sorted([p for p in bdir.iterdir() if p.suffix.lower() in exts and p.is_file()])


def _parse_hhmm(s: str) -> tuple[int, int]:
    s = (s or "00:00").strip()
    parts = s.replace(".", ":").split(":")
    h = int(parts[0]) if parts else 0
    m = int(parts[1]) if len(parts) > 1 else 0
    return h % 24, min(59, max(0, m))


def horario_autorizado() -> bool:
    sh, sm = _parse_hhmm(os.environ.get("SENTINEL_HORA_INICIO", "07:00"))
    eh, em = _parse_hhmm(os.environ.get("SENTINEL_HORA_FIN", "22:00"))
    now = datetime.now().time()
    t0 = datetime.now().replace(hour=sh, minute=sm, second=0, microsecond=0).time()
    t1 = datetime.now().replace(hour=eh, minute=em, second=0, microsecond=0).time()
    if t0 <= t1:
        return t0 <= now <= t1
    return now >= t0 or now <= t1


def motion_detected(prev_gray, gray, thresh: float, min_area: float) -> bool:
    import cv2

    diff = cv2.absdiff(prev_gray, gray)
    _, th = cv2.threshold(diff, thresh, 255, cv2.THRESH_BINARY)
    th = cv2.dilate(th, None, iterations=2)
    cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in cnts:
        if cv2.contourArea(c) >= min_area:
            return True
    return False


def send_telegram_security_alert(photo_path: Path, caption: str) -> None:
    import requests

    token = (os.environ.get("TELEGRAM_TOKEN") or "").strip()
    chat = (os.environ.get("TELEGRAM_ADMIN_ID") or "").strip().replace("'", "").replace('"', "")
    if not token or not chat:
        logger.error("Falta TELEGRAM_TOKEN o TELEGRAM_ADMIN_ID para alerta Sentinel.")
        return
    cap = (caption or "")[:1024]
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    with photo_path.open("rb") as f:
        r = requests.post(url, data={"chat_id": chat, "caption": cap}, files={"photo": f}, timeout=90)
    if r.status_code != 200:
        logger.error("sendPhoto falló: %s %s", r.status_code, r.text[:500])


def on_javier_identified() -> None:
    import ia_brain
    import ia_local_store
    import ia_audio_out

    ctx = "Sujeto identificado: Javier. Acción: Saludo inicial proactivo (Nora Light / Gemini)."
    ia_brain.dispatch_vision_event(ctx)
    resumen = ia_local_store.flash_resumen_pendientes_texto()
    saludo = os.environ.get("NORA_VOZ_SALUDO") or ia_audio_out.GREETING_JAVIER_DEFAULT
    texto = f"{saludo} {resumen}".strip()
    if not ia_audio_out.speak(texto):
        logger.warning("No se pudo reproducir voz (pyttsx3/gTTS). Texto: %s", texto[:120])


def on_sentinel_intruder(frame_copy: Path, security_dir: Path) -> None:
    import ia_brain

    security_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = security_dir / f"intruso_{stamp}.jpg"
    shutil.copy2(frame_copy, dest)
    analysis = ia_brain.analyze_security_scene_image(str(dest))
    caption = (
        "🛡️ Nora Sentinel (Nora Light) — Intruso o sujeto desconocido "
        "(horario no autorizado).\n"
        f"Análisis de escena: {analysis}"
    )
    try:
        send_telegram_security_alert(dest, caption)
    except Exception as e:
        logger.error("Alerta Telegram: %s", e)
    ia_brain.dispatch_vision_event(
        f"Sujeto Desconocido. Acción: alerta enviada; captura en {dest.name}"
    )


def open_capture():
    import cv2

    url = (os.environ.get("NORA_CAMERA_URL") or "").strip()
    if url:
        cap = cv2.VideoCapture(url)
    else:
        idx = int(os.environ.get("NORA_CAMERA_INDEX", "0"))
        cap = cv2.VideoCapture(idx)
    if not cap.isOpened():
        raise RuntimeError("No se pudo abrir la cámara (índice o URL).")
    return cap


def run_sentinel_loop() -> None:
    import ia_brain
    import cv2

    BIOMETRIA_JAVIER_DIR, SECURITY_LOGS_DIR, TMP_DIR = _paths()
    ref_paths = _list_ref_images(BIOMETRIA_JAVIER_DIR)
    if not ref_paths:
        logger.error(
            "No hay imágenes en %s — coloque fotos de referencia de Javier (jpg/png).",
            BIOMETRIA_JAVIER_DIR,
        )
        return
    if not os.environ.get("GEMINI_API_KEY"):
        logger.error("Nora Light requiere GEMINI_API_KEY en el entorno.")
        return

    j_cool = float(os.environ.get("NORA_JAVIER_COOLDOWN_SEC", "120"))
    s_cool = float(os.environ.get("NORA_SENTINEL_COOLDOWN_SEC", "300"))
    frame_sleep = float(os.environ.get("NORA_BIOMETRIA_FRAME_SEC", "0.08"))
    mot_th = float(os.environ.get("NORA_MOTION_THRESHOLD", "25"))
    mot_area = float(os.environ.get("NORA_MOTION_MIN_AREA", "8000"))
    api_gap = float(os.environ.get("NORA_MIN_SECONDS_BETWEEN_API", "12"))
    conf_min = float(os.environ.get("NORA_GEMINI_CONFIDENCE_MIN", "85"))

    last_j = 0.0
    last_s = 0.0
    last_api = 0.0
    cap = open_capture()
    frame_path = TMP_DIR / "nora_light_frame.jpg"
    prev_gray = None

    logger.info(
        "Nora Light activo (movimiento OpenCV + identidad Gemini). Refs=%s. Horario %s–%s.",
        len(ref_paths),
        os.environ.get("SENTINEL_HORA_INICIO", "07:00"),
        os.environ.get("SENTINEL_HORA_FIN", "22:00"),
    )

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.5)
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            if prev_gray is None:
                prev_gray = gray
                time.sleep(frame_sleep)
                continue

            moved = motion_detected(prev_gray, gray, mot_th, mot_area)
            prev_gray = gray.copy()
            if not moved:
                time.sleep(frame_sleep)
                continue

            now = time.time()
            if now - last_api < api_gap:
                time.sleep(frame_sleep)
                continue

            cv2.imwrite(str(frame_path), frame)
            last_api = now

            g = ia_brain.gemini_identity_match_nora_light(str(frame_path), ref_paths)
            logger.info(
                "Gemini identidad: human=%s target=%s conf=%.1f",
                g.get("human_present"),
                g.get("is_target"),
                g.get("confidence", 0),
            )

            if g.get("human_present") and g.get("is_target") and float(g.get("confidence") or 0) >= conf_min:
                if now - last_j >= j_cool:
                    last_j = now
                    on_javier_identified()
                time.sleep(1.0)
                continue

            if (
                g.get("human_present")
                and not g.get("is_target")
                and float(g.get("confidence") or 0) >= 30
                and not horario_autorizado()
            ):
                if now - last_s >= s_cool:
                    last_s = now
                    on_sentinel_intruder(frame_path, SECURITY_LOGS_DIR)

            time.sleep(frame_sleep)
    finally:
        cap.release()


if __name__ == "__main__":
    run_sentinel_loop()
