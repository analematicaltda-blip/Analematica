# Auditoría privada de recuperación — corte 25

Se implementó trazabilidad transaccional de emisión, regeneración y uso de
códigos ERP. El plan maestro continúa en curso; no se certifica producción.

## Resultado funcional

ErpSecurityEvent registra un UUID, actor interno, tipo, fecha y referencias
opcionales de factor/desafío. No admite campos de payload y no guarda contraseñas,
códigos, semillas, cookies ni datos de red. No usa relaciones con eliminación
en cascada. La emisión, rotación o uso exitosos escriben el evento dentro de
su transacción. Si falla la auditoría, se revierte el cambio SQL y no se
completa la operación. La caché TOTP puede haber rechazado ya la reutilización:
se espera un código nuevo, no se vacía esa protección para reintentar.

GET /api/v1/erp-session/security-events/ requiere sesión ERP válida y devuelve
solo id, tipo y fecha de los últimos 20 eventos del propio usuario. No permite
elegir otro actor. La interfaz permite consultar ese historial sin exponer
referencias internas de factores o desafíos. Conserva la paleta azul y blanco.

El modelo rechaza edición y borrado por las operaciones normales de Django.
Esto no es almacenamiento inmutable: SQL directo o un administrador de DB
pueden alterarlo. Permisos SQL, retención, respaldo y exportación independiente
siguen siendo tareas productivas. No se envían mensajes ni alertas externas.

## Migración y verificación

Nueva migración fresh-local turismo.0006_erpsecurityevent, aplicada solo en
las dos instalaciones temporales seleccionadas; ambas sin deriva de modelos
y con comprobación de esquema lista. Sin migrar bases heredadas o de clientes.

- 53 pruebas de sesión/MFA/recuperación/auditoría aprobadas. Cinco nuevas cubren
  eventos de emisión/rotación/uso, reversión ante fallo de auditoría en emisión
  y consumo, bloqueo de edición/borrado y aislamiento/límite del historial.
- 27 regresiones de identidad/cotizaciones, cinco del gateway y 11 del ERP
  migrado aprobadas: 96 pruebas Python en estos conjuntos.
- Cinco escenarios PostgreSQL concurrentes aprobados, ahora comprobando también
  un único evento para cada operación de recuperación/emisión aceptada.
- 24 comprobaciones HTTPS con React, Django y Nginx, incluido historial privado
  y evento de uso; TypeScript estricto y empaquetado correctos.
- git diff --check correcto. Cuentas y secretos sintéticos únicamente.

La prueba PostgreSQL usa esquema mínimo y conexiones independientes en hilos;
no acredita todos los módulos migrados, varios procesos WSGI o carga sostenida.
La evidencia web no sustituye pruebas en teléfonos físicos.

## Pendientes

Intentos fallidos y demás accesos; notificaciones al titular; entrega supervisada
a SOC; permisos SQL y retención; recuperación de ambos factores; contraseña por
canal verificado; custodia de llaves; dispositivos; identidad compartida y demás
módulos del plan maestro. Los registros de este corte cubren solo las operaciones
de recuperación aceptadas y no constituyen un SOC completo.
Sin commit, push ni despliegue productivo. Ver audit-recovery-evidence-25.json.
