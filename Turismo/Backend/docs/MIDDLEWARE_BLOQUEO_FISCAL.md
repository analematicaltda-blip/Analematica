# ESPECIFICACIÓN: MIDDLEWARE DE BLOQUEO FISCAL — SARITA 2026

## 🔒 Bloque 7: Restricciones Absolutas de Escritura

Para garantizar la inmutabilidad de los estados financieros ya reportados, se implementará un middleware que intercepte cualquier intento de modificación en el ORM.

### 1. Modelos Afectados
- `JournalEntry` / `LedgerEntry`
- `FacturaVenta` / `ReciboCaja`
- `TaxTransaction`
- `PayrollRecord`

### 2. Lógica del Middleware (`FiscalLockInterceptor`)
```python
def validate_fiscal_lock(instance):
    target_date = getattr(instance, 'entry_date', instance.created_at.date())
    period = FiscalPeriod.objects.get_for_date(target_date)

    if period.status in ["CLOSED", "LOCKED"]:
        raise FiscalPeriodLockedError(
            f"OPERACIÓN RECHAZADA: El periodo {period.id} está cerrado. "
            "No se permiten inserciones, ediciones ni borrados."
        )
```

## 🚫 Matriz de Acciones Prohibidas
| Acción | Estado: OPEN | Estado: CLOSED | Estado: LOCKED |
| :--- | :---: | :---: | :---: |
| Crear Asiento | ✅ Permitido | ❌ Bloqueado | ❌ Bloqueado |
| Editar Monto | ✅ Permitido | ❌ Bloqueado | ❌ Bloqueado |
| Eliminar Registro | ✅ Permitido | ❌ Bloqueado | ❌ Bloqueado |
| Reversar | ✅ Permitido | ⚠️ Periodo Actual | ⚠️ Periodo Actual |

---
**Resultado:** Cero posibilidad de "Ajustes bajo la mesa" en periodos contables cerrados.
