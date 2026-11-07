# syntax=docker/dockerfile:1
FROM python:3.12-slim AS common
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 MPLCONFIGDIR=/tmp/matplotlib
WORKDIR /srv

FROM common AS analematica
COPY --chown=10001:10001 BACKEND/ANALEMATICA-BACKEND /srv/BACKEND/ANALEMATICA-BACKEND
COPY BACKEND/deployment/requirements-analematica.txt /tmp/requirements.txt
RUN --mount=type=secret,id=proxy_ca \
    if [ -s /run/secrets/proxy_ca ]; then export PIP_CERT=/run/secrets/proxy_ca; fi; \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    groupadd -g 10001 backend && useradd -u 10001 -g backend -m backend
WORKDIR /srv/BACKEND/ANALEMATICA-BACKEND
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "deployment.api:app", "--host", "0.0.0.0", "--port", "8000"]

FROM common AS sgacd
COPY --chown=10001:10001 BACKEND/SGA-CD-BACKEND /srv/BACKEND/SGA-CD-BACKEND
COPY --chown=10001:10001 DB/SGA-CD-DB.git /srv/DB/SGA-CD-DB.git
COPY --chown=10001:10001 BACKEND/deployment/sgacd_entrypoint.py /srv/entrypoint.py
RUN --mount=type=secret,id=proxy_ca \
    if [ -s /run/secrets/proxy_ca ]; then export PIP_CERT=/run/secrets/proxy_ca; fi; \
    pip install --no-cache-dir -r /srv/BACKEND/SGA-CD-BACKEND/requirements.txt && \
    groupadd -g 10001 backend && useradd -u 10001 -g backend -m backend && \
    mkdir -p /state && chown backend:backend /state
ENV PYTHONPATH=/srv/BACKEND/SGA-CD-BACKEND:/srv/DB/SGA-CD-DB.git
WORKDIR /state
USER 10001:10001
EXPOSE 8000
CMD ["python", "/srv/entrypoint.py"]

FROM common AS tourism
COPY --chown=10001:10001 WALLET-BACKEND /srv/WALLET-BACKEND
COPY --chown=10001:10001 BACKEND/SGA-TUR-BAKEND /srv/BACKEND/SGA-TUR-BAKEND
COPY --chown=10001:10001 BACKEND/SGA-ERP-TUR-BAKEND /srv/BACKEND/SGA-ERP-TUR-BAKEND
COPY --chown=10001:10001 BACKEND/ANALEMATICA-BACKEND /srv/BACKEND/ANALEMATICA-BACKEND
COPY --chown=10001:10001 BACKEND/deployment /srv/BACKEND/deployment
RUN --mount=type=secret,id=proxy_ca \
    if [ -s /run/secrets/proxy_ca ]; then export PIP_CERT=/run/secrets/proxy_ca; fi; \
    pip install --no-cache-dir -r /srv/BACKEND/deployment/requirements-tourism.txt && \
    groupadd -g 10001 backend && useradd -u 10001 -g backend -m backend && \
    mkdir -p /srv/BACKEND/SGA-TUR-BAKEND/logs /state && \
    chown -R backend:backend /srv/BACKEND/SGA-TUR-BAKEND/logs /state
ENV PYTHONPATH=/srv/BACKEND/SGA-TUR-BAKEND:/srv/BACKEND/deployment
WORKDIR /state
USER 10001:10001
EXPOSE 8000
CMD ["python", "/srv/BACKEND/deployment/tourism_entrypoint.py"]
