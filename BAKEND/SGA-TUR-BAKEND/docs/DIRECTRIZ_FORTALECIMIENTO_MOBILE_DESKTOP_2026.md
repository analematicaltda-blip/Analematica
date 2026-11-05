# DIRECTRIZ MAESTRA DE FORTALECIMIENTO INTEGRAL: ECOSISTEMA MOBILE & DESKTOP 2026

**Objetivo:** Elevar las capas de cliente (React Native & Electron) al estándar de excelencia del Frontend Oficial, garantizando interoperabilidad total y operatividad de la jerarquía de Agentes IA (N1-N7) desde cualquier dispositivo.

---

## 1. INVENTARIO DE PÁGINAS Y PANELES REQUERIDOS (UX PARITY)

Para lograr una gestión fluida y sin interrupciones, ambas aplicaciones DEBEN implementar las siguientes interfaces, consumiendo el 100% de las APIs del Backend Django:

### VÍA 1: CIUDADANOS / TURISTAS (CONSUMO & EXPERIENCIA)
1.  **Dashboard del Viajero:** Saldo de Wallet, últimas experiencias y recomendaciones IA.
2.  **Marketplace de Experiencias:** Catálogo con filtros avanzados, precios dinámicos y disponibilidad real.
3.  **Pasaporte Digital (NFC/QR):** Identidad soberana, historial de sellos y logros nómadas.
4.  **Gestor de Reservas:** Estado de pagos, tickets electrónicos y chat con el operador.
5.  **Billetera Multi-Moneda:** Recargas, transferencias P2P y recompensas por sostenibilidad.
6.  **SARITA Delivery:** Interfaz de pedidos en tiempo real (Restaurantes/Productos locales).
7.  **Centro de Notificaciones IA:** Alertas proactivas de clima, eventos y seguridad.

### VÍA 2: PRESTADORES / EMPRESARIOS (ERP "MI NEGOCIO")
1.  **Dashboard Operativo:** Resumen de ventas, órdenes del día y estado de recursos (Hoteles/Transporte).
2.  **Módulo GESCONTABLE:**
    *   Libro Diario, Libro Mayor y Balance General (Generados por Soldados N6).
    *   Estado de Resultados (P&L) y Conciliación Bancaria.
3.  **CRM Comercial:** Gestión de prospectos, embudos de venta y fidelización de clientes.
4.  **Gestión Archivística:** Subida de documentos con SHA-256 e historial de auditoría inmutable.
5.  **Calendario de Reservas:** Vista de disponibilidad por fechas, bloqueos y check-ins.
6.  **Panel de Transmisión Live:** Herramientas para "Live Streaming" de experiencias turísticas.

### VÍA 3: GUBERNAMENTAL / ADMIN (TORRE DE CONTROL)
1.  **Global Analytics:** Mapas de calor de flujo turístico, ingresos por categoría y predicción de demanda.
2.  **Cerebro de Gobernanza IA:** Monitor de salud del sistema, alertas de fraude y cumplimiento normativo.
3.  **Torre de Control SuperAdmin:** Gestión de tenants, suscripciones y configuración global del ecosistema.
4.  **Open Data Portal:** Acceso a datasets públicos para investigación y transparencia institucional.

---

## 2. PROTOCOLO DE INTEROPERABILIDAD Y AGENTES IA (N1 - N7)

La jerarquía de agentes debe ser operable desde las aplicaciones mediante el **AI Agent Interface (AAI)** integrado en el Shared SDK:

1.  **Consumo de APIs de Misión:**
    *   Toda acción que requiera un Agente (ej: "SADI, genera mi balance del mes") debe enviar una solicitud al endpoint `/api/v1/ai-agents/mission/`.
    *   El cliente debe mostrar el estado de la misión: `PLANNING` (N1), `DELEGATING` (N2-N5), `EXECUTING` (N6), `VERIFYING` (N7).
2.  **Operatividad del Soldado de Oro (N6):**
    *   Las interfaces de contabilidad y ventas deben activar disparadores que invoquen a los Soldados N6 en el backend, garantizando que cada clic en el cliente resulte en una transacción atómica y auditada.
3.  **Interoperabilidad Total:**
    *   Si un Prestador inicia una conciliación en Desktop, debe poder ver el progreso y finalizarla desde su Mobile App. El estado de la misión reside en la base de datos centralizada (Backend), no en el cliente.

---

## 3. ESTÁNDARES TÉCNICOS DE ROBUSTEZ

1.  **SDK httpClient:** Debe usar interceptores para manejar fallos de red silenciosamente, reintentando peticiones críticas de los agentes.
2.  **Sincronización de Archivos:** Desktop usará el puente de hardware para escaneo masivo, mientras que Mobile usará la cámara con OCR para digitalización inmediata. Ambos deben subir a la misma estructura de S3.
3.  **Hardware Real:** La versión Desktop DEBE estar vinculada a drivers de impresión térmica y escáneres ID para evitar el ingreso manual de datos en el ERP.

---

## 4. CONCLUSIÓN DE LA DIRECTRIZ

Para que las aplicaciones sean perfectas, la implementación debe seguir el principio de **"Cliente Delgado, Cerebro Grueso"**. No se permite lógica de cálculo en React Native ni en Electron; el cliente solo captura la intención del usuario y muestra el resultado procesado por el Backend y sus Agentes IA.

---
*Directriz emitida para el fortalecimiento del ecosistema SARITA 2026.*
