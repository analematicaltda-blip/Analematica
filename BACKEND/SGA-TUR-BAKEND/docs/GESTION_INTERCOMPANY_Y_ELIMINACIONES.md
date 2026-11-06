# GESTIÓN INTERCOMPANY Y ELIMINACIONES — SARITA 2026

## 🎯 Objetivo (Bloque 8)
Neutralizar automáticamente las transacciones entre empresas del Holding (Cuentas Espejo) para evitar la inflación artificial del balance consolidado.

## 🏗️ 8.1 Identificación de Operaciones Intercompany

Toda transacción que involucre a otra entidad del Holding debe ser marcada con los siguientes metadatos:
- `is_intercompany = True`
- `counterparty_tenant_id = 'UUID-B'`
- `consolidation_code = 'IC-DEBT-01'`

## 🔄 8.2 Motor de Eliminación Automática

El `IntercompanyEliminator` ejecutará la siguiente lógica durante la consolidación:

1.  **Detección de Espejos:** El sistema busca saldos con el mismo `consolidation_code` entre el Tenant A y el Tenant B.
2.  **Validación de Montos:** `If TenantA.Balance(IC-DEBT-01) + TenantB.Balance(IC-CRED-01) == 0`.
3.  **Generación de Asiento de Eliminación:**
    - El sistema crea un asiento virtual en el Snapshot consolidado que neutraliza ambos saldos.
    - Si los montos no coinciden, se genera una **Alerta de Diferencia Intercompany** nivel `HIGH`.

## 📜 12. Reglas de Consolidación por Participación

| Método | Aplicación | Lógica |
| :--- | :--- | :--- |
| **Integración Global** | Control > 50% | Suma 100% de activos/pasivos + Cálculo de Minoritarios. |
| **Integración Proporcional**| Joint Ventures | Suma ponderada según el % de participación. |
| **Método de Participación** | Influencia < 20% | Registro en una sola línea de inversión en el Activo. |

---
**Resultado:** Cero riesgo de duplicidad de ingresos o activos dentro del grupo corporativo.
