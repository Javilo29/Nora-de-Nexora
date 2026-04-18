FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema para Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Puerto que usa PTB (Render usa PORT, Fly usa 8080 por defecto)
ENV PORT=8080

EXPOSE 8080

CMD ["python", "bot_simple.py"]
