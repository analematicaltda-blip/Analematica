# GOBERNANZA DE EJECUCIÓN Y PROTOCOLO ERP — SARITA 2026

## 🛡️ Bloque 3: Autorización por Módulo
Cada Soldado N6 es ahora el **Guardián Final** del permiso.

- **Lógica de Validación:** El soldado no hereda permisos del sargento; los valida él mismo usando el contexto del usuario.
- **Mapeo:**
    - `SoldadoRegistroGasto` -> `contable.write_expense`
    - `SoldadoLiquidacion` -> `payroll.execute_payout`

## ⛓️ Bloque 4: Jerarquía Operacional Inviolable
Se prohíbe la ejecución de soldados fuera del flujo militar:

1.  **Orden Raíz:** `GovernanceKernel` autoriza la intención.
2.  **Planificación:** `Capitán` desglosa en tareas.
3.  **Supervisión:** `Sargento` coordina la ejecución de exactamente N soldados.
4.  **Ejecución:** El `Soldado` es el único que toca el ORM.

*Cualquier llamada directa al Soldado desde una API View resultará en una excepción `OperationalHierarchyViolation`.*

## ⚙️ Bloque 5: Integración Total ERP (Outbox + Idempotencia)

### Protocolo de Consistencia:
1.  **Idempotencia:** Uso obligatorio de una `idempotent_key` (ej: hash de la factura). Si el soldado recibe la misma llave, retorna el ID de la entidad ya creada.
2.  **Outbox:** El soldado no emite al EventBus; inserta en `OutboxEvent`. El **OutboxRelay** garantiza que el mensaje llegue al Bus real exactamente una vez.
3.  **Versión:** Se valida que la entidad no haya sido modificada por otro agente (`version_check`).

---
**Resultado:** Una cadena de mando digital que garantiza que cada cambio en el ERP sea autorizado, ordenado y consistente.
