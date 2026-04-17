# Nora / Nexora — Repl.it (Replit) listo

Arrastre la carpeta del proyecto (por ejemplo `D:\NORA_NEXORA_FINAL` o `D:\Biblioteca\Escritorio\NORA_NEXORA_FINAL`) a un **Repl** nuevo como raíz del repositorio.

## Entorno (Secrets / `.env`)

Defina en **Secrets** (o archivo `.env` en la raíz) las variables que use cada módulo:

| Variable | Obligatorio | Uso |
|----------|-------------|-----|
| `GEMINI_API_KEY` | Sí (cerebro + Nora Light) | Chat fallback, visión, `ia_biometria` identidad |
| `GROQ_API_KEY` | Recomendado | Chat principal `ia_brain` |
| `TELEGRAM_TOKEN` | Si usa el bot | `ia_telegram_bot` |
| `TELEGRAM_ADMIN_ID` | Si usa el bot | ID numérico de Javier (solo admin actual) |
| `SUPABASE_URL` | Opcional | Email / historial Supabase |
| `SUPABASE_KEY` | Opcional | Cliente Supabase |

## Nora Light (cámara opcional en Repl)

| Variable | Default | Descripción |
|----------|---------|-------------|
| `NORA_CAMERA_INDEX` | `0` | Índice de cámara (si el Repl expone vídeo) |
| `NORA_GEMINI_CONFIDENCE_MIN` | `85` | Confianza mínima para considerar a Javier |
| `NORA_MIN_SECONDS_BETWEEN_API` | `12` | Mínimo entre llamadas a Gemini (coste / cuota) |
| `NORA_MOTION_THRESHOLD` | `25` | Sensibilidad movimiento |
| `NORA_MOTION_MIN_AREA` | `8000` | Área mínima de contorno (píxeles) |
| `SENTINEL_HORA_INICIO` | `07:00` | Inicio horario “autorizado” |
| `SENTINEL_HORA_FIN` | `22:00` | Fin horario autorizado |

**Nota:** En Replit suele no haber cámara local; `ia_biometria.py` es principalmente para PC con Windows/Linux y webcam o URL `NORA_CAMERA_URL`.

## Instalación de dependencias

```bash
pip install -r requirements.txt
# Si usar Sentinel / cámara (OpenCV pequeño + voz opcional):
pip install -r requirements-vision.txt
```

No instale `tensorflow`, `keras` ni `deepface` en el Repl salvo necesidad excepcional; el modo **Nora Light** no los usa.

## Arranque típico

- Dashboard: `streamlit run Guiones/ia_dashboard.py` (ajuste rutas según Repl).
- Bot Telegram: `python Guiones/ia_telegram_bot.py`
- Sentinel Light: `python Guiones/ia_biometria.py`
