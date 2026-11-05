# DIRECTRICES MAESTRAS DE ARQUITECTURA Y DESARROLLO — SARITA ERP

## 1. PRINCIPIO FUNDAMENTAL DE ARQUITECTURA
### 1.1 Backend como única fuente de verdad (SOT)
**Regla Crítica:** TODO se ejecuta en el backend. Los clientes (Web, Mobile, Desktop) NUNCA contienen lógica de negocio.
- **Reglas contables:** Backend.
- **Validaciones DIAN:** Backend.
- **Estados de documentos:** Backend.
- **Cálculo financiero:** Backend.
- **Auditoría y Blockchain:** Backend.

## 2. ARQUITECTURA GENERAL DEL ECOSISTEMA
- **Infraestructura:** Load Balancer -> API Gateway -> Backend Django.
- **Tecnologías:** PostgreSQL, Redis, Celery, S3/MinIO.
- **Clientes:** Web App (Next.js), Mobile (Expo/React Native), Desktop (Electron).

## 3. DIRECTRICES DEL BACKEND API
- **Tecnología:** Python/Django, DRF, PostgreSQL, Redis, JWT.
- **Estándar de Endpoints:** `/api/v1/{modulo}/{recurso}/`.
- **Formato de Respuesta:** `{ "status": "success", "message": "...", "data": {}, "errors": null }`.
- **Seguridad:** JWT, Multi-tenant obligatorio (X-Tenant-ID), RBAC, Auditoría Total.

## 4. DIRECTRICES DEL FRONTEND (Web, Mobile, Desktop)
- **Lógica:** El frontend NO calcula nada importante. Todo viene del backend.
- **Cliente API:** Centralizado vía Shared SDK.
- **Mobile:** React Native/Expo, Offline First con SQLite y Sync Engine.
- **Desktop:** Electron con Next.js, integración con hardware local (POS, impresoras, escáneres).

## 5. GESTIÓN DOCUMENTAL Y CONTABLE
- **Archivística:** Ley 594, ISO 15489. UUID, SHA256, Merkle Root en Blockchain.
- **Contabilidad:** NIIF. Motor Ledger inmutable con Chained Hashing. Asientos automáticos por cada evento financiero.

## 6. OBSERVABILIDAD Y CI/CD
- **Monitoreo:** Prometheus, Grafana, Sentry.
- **Pipeline:** GitHub Actions -> Docker -> CI/CD. Cobertura de tests > 80%.
- **Versionado:** API versioning (/api/v1/, /api/v2/).
