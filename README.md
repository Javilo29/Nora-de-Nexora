# Nora - Nexora Visual SaaS v12

Nora es una asistente administrativa de IA multi-cliente diseñada para Nexora Visual. Este repositorio contiene el núcleo cognitivo y las interfaces de conexión.

## Características SaaS Ready
- **Aislamiento Multi-Tenant**: Cada usuario/cliente tiene su propio historial y contexto aislado en memoria.
- **FAQ de Negocio**: Sistema de respuestas rápidas para consultas frecuentes sobre Nexora Visual.
- **Optimización de Costos**: Filtro de intención local que evita llamadas innecesarias a la API de Groq para respuestas de cortesía.
- **Branding Profesional**: Personalidad configurada para representar oficialmente a Nexora Visual con un tono ejecutivo.

## Estructura del Proyecto
- `nora_cloud_bot.py`: Interface de Telegram configurada para Render.
- `app_local.py`: Servidor local para interacción física y panel de control.
- `Guiones/NoraCore/`: Núcleo de inteligencia.
    - `nora_brain.py`: Cerebro cognitivo.
    - `nora_memory_manager.py`: Gestión de memoria multi-cliente.
    - `nora_faq.py`: Base de conocimientos de la empresa.
    - `nora_vision.py`: Procesamiento de imágenes y rostros.
    - `nora_network.py`: Escaneo de red local IoT.

## Configuración
Asegúrese de tener las siguientes variables en su archivo `.env`:
- `TELEGRAM_TOKEN`: Token de su bot de Telegram.
- `GROQ_API_KEY`: Llave de API para el modelo Llama 4 Scout.
- `RENDER_EXTERNAL_URL`: URL de su servicio en Render (para Webhooks).

## Instalación
```bash
pip install -r requirements.txt
```

---
© 2026 Nexora Visual - Todos los derechos reservados.
