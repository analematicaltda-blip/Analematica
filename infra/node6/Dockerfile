FROM python:3.12-slim
RUN --mount=type=secret,id=proxy_ca \
    if [ -f /run/secrets/proxy_ca ]; then export PIP_CERT=/run/secrets/proxy_ca; fi; \
    apt-get update && apt-get install -y --no-install-recommends ffmpeg fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /tmp/requirements.txt
RUN --mount=type=secret,id=proxy_ca \
    if [ -f /run/secrets/proxy_ca ]; then export PIP_CERT=/run/secrets/proxy_ca; fi; \
    pip install --no-cache-dir -r /tmp/requirements.txt
WORKDIR /app
COPY engine.py /app/infra/node6/engine.py
COPY main.py /app/infra/node6/main.py
COPY youtube.py /app/infra/node6/youtube.py
COPY studio.html studio.js studio.css /app/infra/node6/
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 NODE6_OUTPUT=/state/generated
EXPOSE 8606
CMD ["uvicorn","infra.node6.main:app","--host","0.0.0.0","--port","8606","--no-access-log"]
