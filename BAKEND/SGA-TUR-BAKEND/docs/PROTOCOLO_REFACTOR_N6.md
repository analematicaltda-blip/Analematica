# PROTOCOLO DE REFACTOR OBLIGATORIO: SOLDADOS N6 — SARITA 2026

## 📜 Propósito
Convertir microtareas informativas en ejecutores atómicos, determinísticos y auditables para la producción masiva.

## 🛠️ Checklist de 9 Etapas por Soldado

| Etapa | Descripción | Estado |
| :--- | :--- | :---: |
| **1. Auditoría** | Identificar dependencias externas y retornos estáticos actuales. | ⬜ |
| **2. Aislamiento** | Asegurar que solo se modifique un Agregado Lógico (Model). | ⬜ |
| **3. Atomaticidad** | Implementar `with transaction.atomic()`. | ⬜ |
| **4. Validación** | Insertar `raise DeterministicValidationError` ante inconsistencias. | ⬜ |
| **5. EventBus** | Emitir evento estructurado post-persistencia. | ⬜ |
| **6. Auditoría SHA** | Registrar en `RegistroMicroTarea` con firma SHA-256. | ⬜ |
| **7. Idempotencia** | Verificar existencia previa de `micro_tarea_id`. | ⬜ |
| **8. Test Unitario** | Probar éxito, fallo, duplicidad y rollback. | ⬜ |
| **9. Integración** | Verificar flujo real desde el Sargento supervisor. | ⬜ |

## 🏗️ Ejemplo de Diseño (SoldadoRegistroIngreso)

### Capa 4: Validación Previa
```python
def validate(self, params):
    if not params.get('tenant_id'): raise DeterministicValidationError("tenant_id missing")
    if Decimal(params.get('total')) <= 0: raise DeterministicValidationError("Total must be > 0")
```

### Capa 6: Auditoría SHA-256
```python
def generate_integrity_hash(self, params, result):
    payload = f"{params}{result}{timezone.now()}"
    return hashlib.sha256(payload.encode()).hexdigest()
```

### Capa 5: Payload de Evento
```json
{
  "event_name": "ACCOUNTING_ENTRY_CREATED",
  "entity_id": "UUID-V4",
  "tenant_id": "TENANT-ID",
  "correlation_id": "CID-XXX",
  "timestamp": "ISO-8601"
}
```

---
**Firmado:** Jules, Software Engineer Audit.
