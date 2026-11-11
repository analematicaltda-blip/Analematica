FROM python:3.12-slim

WORKDIR /srv/BACKEND/SGA-CD-BACKEND

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY BACKEND/SGA-CD-BACKEND/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY BACKEND/SGA-CD-BACKEND .
COPY BACKEND/ANALEMATICA-BACKEND/agents/legacy_command_staff.py /srv/BACKEND/ANALEMATICA-BACKEND/agents/legacy_command_staff.py
COPY BACKEND/ANALEMATICA-BACKEND/agents/contracts /srv/BACKEND/ANALEMATICA-BACKEND/agents/contracts

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
