FROM python:3.12-slim

WORKDIR /app

# Instalar FFmpeg y dependencias de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar librerias Python
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    requests \
    pydantic \
    pillow

# COPIAR EL CODIGO FUENTE (main.py)
COPY . .

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]