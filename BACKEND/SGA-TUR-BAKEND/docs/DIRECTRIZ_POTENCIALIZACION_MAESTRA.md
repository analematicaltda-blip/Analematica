# DIRECTRIZ DE IMPLEMENTACIÓN MAESTRA — SARITA WORLD-CLASS 2026

## 1. Backend (El Cerebro)
- **Criptografía N6:** Aplicar estándar Oro V2 en todas las transacciones de base de datos.
- **Resiliencia:** Implementar Multi-DB para aislamiento total de la Wallet y Delivery.
- **Performance:** Optimizar APIs mediante Celery/Redis para respuestas < 200ms.

## 2. Frontend Web (El Portal)
- **Consistencia:** Uso obligatorio del Shared SDK para todas las peticiones.
- **UX:** Implementar carga asíncrona avanzada (SWR) para dashboards instantáneos.

## 3. Mobile APK (El Brazo)
- **Movilidad:** Implementar Sync Engine para operación Offline total en campo.
- **Seguridad:** Activar autenticación biométrica nativa para transacciones críticas.
- **Inteligencia:** Activar Geofencing para detección de proximidad de turistas.

## 4. Desktop (La Estación)
- **Hardware:** Integración nativa con periféricos POS e impresoras fiscales.
- **Estabilidad:** Gestión de persistencia local resiliente a fallos de red.

## 5. Shared SDK (El Pegamento)
- **Tipado:** Sincronización de esquemas de datos Backend -> SDK -> Clientes.
- **Seguridad:** Gestión centralizada de JWT y headers de Multi-tenancy.
