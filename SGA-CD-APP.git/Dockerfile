FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema requeridas por Flet
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || true

# Copiar código fuente
COPY . .

CMD ["python3", "main.py"]
