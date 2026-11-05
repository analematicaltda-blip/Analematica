# BLINDAJE DE CONSISTENCIA GLOBAL — SARITA 2026

## 📜 Propósito (Bloque 1)
Eliminar estados inconsistentes y garantizar que cada cambio en una entidad crítica (Asiento, Factura, Nómina) sea parte de una cadena de integridad inmutable y versionada.

## 🔗 1.1 Versionado Universal y Cadena de Integridad

Cada entidad crítica implementará el siguiente esquema de metadatos de integridad:

| Campo | Tipo | Propósito |
| :--- | :--- | :--- |
| `version` | Integer | Contador incremental de modificaciones. |
| `previous_hash` | Char(64) | Hash SHA-256 del estado anterior de la entidad. |
| `current_hash` | Char(64) | Hash SHA-256 del estado actual (payload + previous_hash). |
| `modified_at` | DateTime | Marca de tiempo UTC de la modificación. |
| `modified_by` | UUID | ID del actor (IA o Humano) que realizó el cambio. |

### Regla de Oro:
**"No existe estado si no está versionado"**. Cualquier entidad detectada con `version=0` o hash nulo será bloqueada por el `GovernanceKernel`.

## ⚡ 1.2 Control de Concurrencia Optimista

Para evitar la pérdida de datos en entornos de alta concurrencia (ej: múltiples agentes operando sobre la misma cuenta), se aplicará la validación de versión en el método `save()`:

```python
def update_entity(entity_id, data, expected_version):
    entity = Model.objects.get(id=entity_id)
    if entity.version != expected_version:
        raise ConcurrencyConflictError(
            f"Conflicto detectado: Versión actual {entity.version} != Esperada {expected_version}"
        )

    # Proceder con la actualización, incrementar versión y recalcular hash
    entity.version += 1
    entity.current_hash = calculate_new_hash(data, entity.current_hash)
    entity.save()
```

---
**Resultado:** Trazabilidad forense total y eliminación de sobrescrituras accidentales.
