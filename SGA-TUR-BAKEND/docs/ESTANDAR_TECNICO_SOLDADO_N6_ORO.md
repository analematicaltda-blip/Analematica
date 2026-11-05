# ESTÁNDAR TÉCNICO: EL SOLDADO DE ORO (N6) — SARITA 2026

## 📜 Objetivo del Estándar (Bloque 1.2)
Garantizar que toda microtarea ejecutada por un agente sea atómica, persistente, auditable e irreversible. Este estándar elimina la "simulación" en los agentes y establece el puente real con el ERP.

## 🏗️ Estructura de las 5 Capas Obligatorias

### 1. Validación Determinística
- **Responsabilidad:** Verificar que la operación sea lícita y los datos íntegros.
- **Regla:** Si la validación falla, se levanta una excepción `DeterministicValidationError`. No se toca la base de datos.

### 2. Operación ORM Atómica
- **Responsabilidad:** Modificar el estado persistente.
- **Implementación:** Todo el cuerpo de ejecución debe estar envuelto en `with transaction.atomic()`.
- **Regla:** Solo se permite modificar un objeto raíz (Agregado Lógico) por soldado.

### 3. Emisión de Evento (EventBus)
- **Responsabilidad:** Notificar al ecosistema sobre el cambio de estado.
- **Implementación:** `EventBus.emit('ACCOUNTING_ENTRY_CREATED', payload)`.
- **Regla:** El evento debe incluir el `correlation_id` para trazabilidad total.

### 4. Registro de Auditoría SHA-256
- **Responsabilidad:** Dejar evidencia forense inmutable de la acción.
- **Implementación:** Crear un `RegistroMicroTarea` con un campo `integrity_hash` que encadene el payload del soldado.

### 5. Resultado Estructurado
- **Responsabilidad:** Informar éxito/fallo de forma técnica al Sargento supervisor.
- **Regla:** Siempre retornar un diccionario con `status`, `entity_id` y `audit_id`.

---

## 🛠️ Blueprint de Código (Refactor de `SoldierTemplate`)

```python
from django.db import transaction
from apps.sarita_agents.models import RegistroMicroTarea
from apps.core_erp.event_bus import EventBus
import hashlib
import json

class SoldadoOroTemplate:
    def execute(self, params):
        # 1. Validación Determinística
        self.validate_data(params)

        try:
            with transaction.atomic():
                # 2. Operación ORM Atómica
                result_data = self.perform_atomic_action(params)

                # 3. Emisión de Evento
                EventBus.emit(self.event_name, {
                    "entity_id": result_data['id'],
                    "tenant_id": params.get('tenant_id'),
                    "correlation_id": params.get('correlation_id')
                })

                # 4. Registro de Auditoría con Hash
                audit = self._log_audit(params, result_data)

                # 5. Resultado Estructurado
                return {
                    "status": "success",
                    "entity_id": result_data['id'],
                    "audit_id": audit.id,
                    "event_emitted": True
                }
        except Exception as e:
             # Rollback automático por transaction.atomic
             return {"status": "failed", "error": str(e)}

    def _log_audit(self, params, result):
        payload = f"{json.dumps(params)}{json.dumps(result)}"
        integrity_hash = hashlib.sha256(payload.encode()).hexdigest()
        return RegistroMicroTarea.objects.create(
            micro_tarea_id=params.get('micro_tarea_id'),
            exitoso=True,
            resultado=result,
            observaciones=f"IntegrityHash: {integrity_hash}"
        )
```

## 🚀 Caso de Uso: `SoldadoRegistroIngreso` (Contabilidad)
Este soldado transformará una intención de cobro en un asiento contable real e irreversible, disparando la actualización del balance de ingresos en la Vía 1 (Gobierno) y Vía 2 (Prestador).
