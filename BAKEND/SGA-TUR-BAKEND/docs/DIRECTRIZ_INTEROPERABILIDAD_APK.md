# DIRECTRIZ DE INTEROPERABILIDAD TOTAL — BACKEND ↔ MOBILE APK

## 1. Unificación de Esquemas (Shared SDK)
- **Protocolo:** Sincronización de tipos TypeScript con modelos Django.
- **Headers:** Inyección mandatoria de `Authorization: Bearer <JWT>` y `X-Tenant-ID`.
- **Estandarización:** Uso único del cliente HTTP del SDK para evitar dispersión de lógica.

## 2. Comunicación en Tiempo Real
- **Tecnología:** WebSockets mediante Django Channels.
- **Consumer:** Suscripción al `TowerConsumer` para recepción de eventos Push.
- **Latencia:** Meta de sincronización de estados < 100ms.

## 3. Estrategia Offline First
- **Persistencia local:** Base de datos SQLite para encolado de transacciones.
- **Sync Engine:** Algoritmo de reconciliación basado en timestamps y hashes de integridad.
- **Conflict Resolution:** Prioridad al servidor con validación de integridad local.

## 4. Seguridad Industrial
- **JWT RS256:** Firmas asimétricas para validación mutua.
- **Biometría:** Desbloqueo nativo para transacciones de Wallet y firmas legales.
- **SSL Pinning:** Certificación de túnel seguro para evitar intercepción de tráfico.

## 5. Optimización de Red
- **Normalización:** Envío de payloads mínimos (JSON plano).
- **Caché:** Implementación de Stale-While-Revalidate (SWR) en el APK.
- **Compresión:** Uso de Brotli/Gzip obligatorio en el servidor.
