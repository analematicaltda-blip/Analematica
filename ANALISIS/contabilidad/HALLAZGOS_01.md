# Hallazgos y primera corrección

## Evidencia reproducida y corregida

1. `JournalEntry.save` consultaba una fila por el UUID recién generado antes de insertarla y provocaba `DoesNotExist`. Ahora verifica existencia de un asiento ya contabilizado sin exigir que exista el nuevo; se conserva el bloqueo de cambios a contabilizados.
2. `JournalService.create_entry` admitía importes sin validación de dominio previa y cuentas de otro tenant en memoria. Se validan decimales exactos, finitud/precisión/rango, lado positivo único, partida doble exacta, cuenta única por tenant y estado activo actual antes de crear el encabezado. Se bloquean cuentas en orden y se exige un periodo abierto inequívoco.
3. El balance dependía del manager ligado al contexto de petición; ahora consulta líneas explícitas del asiento y verifica empresa de línea/cuenta. Se elimina la tolerancia en esa validación.
4. Una línea podía consultar un padre cacheado como borrador aunque otro escritor ya lo hubiera contabilizado. Las guardas ORM de guardar/borrar vuelven a consultar el estado del asiento.

Antes de corregir se reprodujeron 13 errores/subtests en8 pruebas; después pasan9 pruebas sobre modelos reales en SQLite aislado. No son pruebas de concurrencia PostgreSQL ni autorización HTTP. Los importes float o subcentavos se rechazan explícitamente: revisar consumidores que antes enviaban esos valores antes de habilitar su flujo. Este ledger actual tiene precisión de2 decimales; no es soporte multiactivo completo.

## Hallazgos pendientes de corrección con pruebas

- `LedgerEngine.calculate_hash` y `JournalEntry.compute_hash` usan contratos diferentes; el primero no cubre cada cuenta/línea/moneda. Preservar hashes históricos y diseñar una versión compatible.
- La idempotencia de eventos consulta antes de insertar, pero requiere garantía única SQL y comparación del payload bajo concurrencia. Outbox y efectos externos deben revisarse.
- `ContabilidadService.crear_asiento_completo` usa `provider.id` como tenant y no aplica todos los parámetros de actor/periodo: no conectar nuevos flujos sin VerifiedCompanyLink.
- El posteo puede continuar con una tasa1.0 si no encuentra FX y convierte el total a float al emitir evento. Requiere corrección y pruebas de consumidores.
- El posteo usa managers de contexto en otras consultas; aún debe comprobarse completo. Auditoría puede recurrir a un superusuario global; sustituir por actor/sistema explícito autorizado, no identidad inferida.
- La cadena por último asiento no garantiza serialización global de un tenant por bloquear cuentas diferentes; hacen falta ensayos concurrentes y diseño de secuencia/cabecera por empresa.
- `save/delete` no protegen frente a `QuerySet.update`, SQL directo u operadores privilegiados; faltan constraints/permisos/triggers revisados. No se declara inmutabilidad criptográfica absoluta.

## Repetición

```bash
python BACKEND/deployment/tests/accounting_foundation_check.py -v
```

Usa el fixture existente de aislamiento empresarial, con claves de prueba y SQLite en memoria. No factura, contabiliza ventas reales, envía pagos ni cambia bases existentes. No se reemplazó el motor ni se modificó el esquema. Ver matriz para dependencias y criterios de cada corrección restante.
