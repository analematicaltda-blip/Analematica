# INVENTARIO DETALLADO DE SOLDADOS N6 — SARITA 2026

## Matriz de Madurez de Ejecución Atómica (Bloque 1.1)

Este inventario clasifica los agentes de Nivel 6 (Soldados) según su capacidad de ejecución real sobre el estado del sistema, identificando los "Mocks" que deben ser eliminados en la Fase de Transición a Autonomía Determinística.

| Soldado | Dominio | Ejecuta DB | Transacción | Auditoría | EventBus | Estado Real |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `SoldadoRegistroIngreso` | Contabilidad | ⚠️ Parcial | ❌ No | ❌ No | ❌ No | Parcialmente Conectado |
| `SoldadoRegistroGasto` | Contabilidad | ⚠️ Parcial | ❌ No | ❌ No | ❌ No | Parcialmente Conectado |
| `SoldadoConciliacionWallet`| Contabilidad | ❌ No | ❌ No | ❌ No | ❌ No | Informativo / Consulta |
| `SoldadoVerificacionFiscal`| Contabilidad | ❌ No | ❌ No | ❌ No | ❌ No | Informativo / Consulta |
| `SoldadoCierreParcial` | Contabilidad | ❌ No | ❌ No | ❌ No | ❌ No | **Mock** |
| `SoldadoLiquidacion` | Nómina | ✅ Sí | ❌ No | ❌ No | ❌ No | Conectado vía Service |
| `SoldadoPrestaciones` | Nómina | ❌ No | ❌ No | ❌ No | ❌ No | **Mock** |
| `SoldadoNovedades` | Nómina | ❌ No | ❌ No | ❌ No | ❌ No | **Mock** |
| `SoldadoRiesgos` | SST | ❌ No | ❌ No | ❌ No | ❌ No | **Mock** |
| `SoldadoIncidentes` | SST | ❌ No | ❌ No | ❌ No | ❌ No | **Mock** |
| `SoldadoCapacitacion` | SST | ❌ No | ❌ No | ❌ No | ❌ No | **Mock** |
| `SoldadoAlertaSobrecosto` | Financiero | ✅ Sí | ❌ No | ❌ No | ❌ No | Parcialmente Conectado |
| `SoldadoRegistroCredito` | Financiero | ✅ Sí | ❌ No | ❌ No | ❌ No | Conectado Real |
| `SoldadoCalculadorAmort` | Financiero | ❌ No | ❌ No | ❌ No | ❌ No | Informativo |
| `SoldadoAjustadorContable` | Financiero | ❌ No | ❌ No | ❌ No | ❌ No | **Mock** |
| `SoldadoRegistroInventario`| Artesanos | ❌ No | ❌ No | ❌ No | ❌ No | **Mock** |
| `SoldadoSincronizadorCom` | Artesanos | ❌ No | ❌ No | ❌ No | ❌ No | **Mock** |
| `SoldadoRegistroLead` | Comercial | ❌ No | ❌ No | ❌ No | ❌ No | **Mock** |
| `SoldadoBuscadorServicios` | Turista | ❌ No | ❌ No | ❌ No | ❌ No | Informativo |
| `SoldadoGestorReservas` | Turista | ❌ No | ❌ No | ❌ No | ❌ No | **Mock** |

## 🔍 Diagnóstico de Inventario

1.  **Predominancia de Mocks:** El 65% de los soldados auditados son esqueletos que retornan JSON estático. No cumplen con el **Principio de Oro**: *"Un Soldado N6 que no modifique estado persistente es inválido"*.
2.  **Ausencia de Atomaticidad:** Ningún soldado implementa explícitamente `transaction.atomic()` en su capa de `perform_action`, delegando (en el mejor de los casos) al servicio invocado.
3.  **Desconexión del EventBus:** La comunicación es imperativa de arriba hacia abajo. No se emiten eventos de "Tarea Completada" para disparar reacciones en otros dominios.
4.  **Carencia de Auditoría Atómica:** Los registros se hacen a nivel de Sargento (intento), pero no existe un sello de integridad SHA-256 por cada ejecución atómica del soldado.

---
**Resultado:** Se requiere el refactor inmediato de los 40+ agentes bajo el estándar del "Soldado de Oro".
