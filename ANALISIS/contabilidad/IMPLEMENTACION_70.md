# Implementación 70 · Compras, IVA descontable, retenciones y contrapartidas

Se ejecutó el siguiente incremento de R03: un hecho comercial revisado puede causar compras o ventas con cuentas explícitas por componente, IVA descontable/generado y retenciones, usando el ledger canónico. La revisión no escribe; la segunda confirmación del mismo titular realiza el asiento. Una contrapartida también exige dos pasos y preserva el original.

El recorrido nuevo está conectado a las API existentes del ERP y a los comandos corporativos de Analemática. Las pruebas HTTP recorren sesión/vínculo, política persistida, compra, asiento real, recuperación, contrapartida e idempotencia. No se usaron proveedores o cuentas reales.

## Evidencia y límites

- 28 casos específicos nuevos aprobados: compra/venta, tipos de cuenta, empresa ajena, actor diferente, desglose/retención, centavos/redondeo, expiración, cambio de política/cuentas/período, recuperación, contrapartida y rollback integral.
- Dos pruebas nuevas del puente corporativo, con HTTP local real, cubren el recorrido positivo y rechazos de contexto/confirmación.
- Regresión completa: **643 pruebas Python aprobadas en 39 suites**, sin omisiones, incluidas42 pruebas del puente corporativo. Manifiesto estable, hashes de artefactos y fuentes actuales verificados; dependencias compatibles.

[Contrato y operación](OPERACION_HECHOS_TRIBUTARIOS.md) · [Evidencia 70](evidencias/implementacion-70.json).

R03 permanece en ejecución: faltan fuentes nativas, conciliación fiscal unificada, deduplicación entre rutas, devoluciones parciales, interfaz, SQL/concurrencia PostgreSQL y aceptación profesional. El conciliador fiscal anterior no se presenta como compatible con estos hechos nuevos. Las reservas conservan sus restricciones anteriores; no se habilita una doble causación automática.

El resto de hitos no se declara subsanado por este incremento. La base global sigue **61,11 % (44/72)** y aceptación completa **0/24**, al ampliar tareas ya acreditadas. No se suman puntos por repetir pruebas ni por añadir un documento.

Sin commits, push, migraciones de datos reales, cambios de diseño, pagos, emisión fiscal ni envíos DIAN. El trabajo permanece en el árbol actual.
