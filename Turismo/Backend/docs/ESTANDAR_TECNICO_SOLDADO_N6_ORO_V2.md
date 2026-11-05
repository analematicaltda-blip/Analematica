# ESTÁNDAR TÉCNICO: EL SOLDADO DE ORO V2 (N6) — SARITA 2026

## 📜 Propósito (Bloque 1)
Evolucionar la ejecución mínima a un modelo de "Operatividad Integral". Cada soldado es ahora un obrero determinístico, consciente de su dominio, sus límites legales (permisos) y su impacto financiero.

## 🏗️ Estructura Estructural Obligatoria

Cada clase de Soldado N6 debe declarar estáticamente su contexto operativo:

| Atributo | Propósito | Ejemplo |
| :--- | :--- | :--- |
| `domain` | Dominio de negocio raíz. | `CONTABILIDAD` |
| `subdomain` | Área específica de operación. | `INGRESOS` |
| `aggregate_root` | Modelo principal que modifica. | `JournalEntry` |
| `required_permissions`| Lista de permisos necesarios. | `['contabilidad.create_entry']` |
| `event_name` | Evento que emite al éxito. | `ACCOUNTING_ENTRY_CREATED` |
| `supports_reversal` | Si la acción es reversible. | `True` |
| `idempotent_key` | Campo para validar duplicidad. | `factura_id` |

## 🔗 Conciencia Contextual V2

El Soldado ya no es una "caja negra". Al iniciar su ejecución (`perform_action`), debe verificar:

1.  **Mandato de Dominio:** ¿Esta tarea pertenece realmente a mi `domain`?
2.  **Autoridad del Actor:** ¿El `user_id` en los parámetros tiene los `required_permissions` en el Tenant actual?
3.  **Estado del Periodo:** Si es una tarea financiera, ¿el periodo fiscal está `OPEN`?

### 🛠️ Blueprint N6-Oro-V2

```python
class SoldadoOroV2:
    def execute(self, task_params):
        # 1. Validación de Conciencia (Bloque 3)
        self._check_permissions(task_params['user'], self.required_permissions)
        self._check_tenant_isolation(task_params['tenant_id'])

        # 2. Verificación de Idempotencia (Bloque 5)
        if self._already_executed(task_params[self.idempotent_key]):
            return self._return_previous_result()

        with transaction.atomic():
            # 3. Operación ORM Real (Bloque 2)
            entity = self.perform_atomic_action(task_params)

            # 4. Auditoría con Hash Encadenado (Bloque 5)
            self._log_audit(task_params, entity)

            # 5. Registro Outbox (Bloque 5)
            self._register_outbox(self.event_name, entity)

        # 6. Resultado Estructurado V2
        return {
            "status": "READY",
            "domain": self.domain,
            "entity_id": entity.id,
            "correlation_id": task_params['correlation_id']
        }
```

---
**Resultado:** Se elimina el comportamiento de "clase genérica". Cada soldado es un componente especializado del ERP.
