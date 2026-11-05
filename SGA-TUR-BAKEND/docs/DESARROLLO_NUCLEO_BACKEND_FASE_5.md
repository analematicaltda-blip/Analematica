# DESARROLLO DEL NÚCLEO DEL SISTEMA — SARITA PLATFORM (FASE 5)

## 1. Desarrollo del Backend
- **Tecnología:** Python 3.x, Django, Django Rest Framework.
- **Arquitectura:** Basada en servicios y agentes IA.
- **Seguridad:** Autenticación JWT, Autorización RBAC, Protección CSRF/CORS.

## 2. Desarrollo de Base de Datos
- **Motor:** PostgreSQL (Primaria), Redis (Caché/Eventos).
- **Modelo:** Relacional normalizado con soporte Multi-tenant nativo.
- **Integridad:** Transacciones atómicas y logs de auditoría obligatorios.

## 3. Integración Modular
- **Mecanismo:** Event Bus central para comunicación desacoplada.
- **Sincronización:** Patrón Outbox para garantizar consistencia eventual.
- **Componentes:** Servicios internos para contabilidad, archivística y operativa.

## 4. Desarrollo de APIs
- **Estilo:** RESTful JSON.
- **Versionado:** /api/v1/.
- **Validación:** Esquemas de datos estrictos y manejo de errores estandarizado.

## 5. Integraciones Externas
- **Documental:** Almacenamiento S3.
- **Legal:** Conexión con servicios de firma digital y DIAN.
- **Blockchain:** Notarización en red Polygon vía Web3.
- **Notificaciones:** Servicios de correo SMTP y alertas Push.
