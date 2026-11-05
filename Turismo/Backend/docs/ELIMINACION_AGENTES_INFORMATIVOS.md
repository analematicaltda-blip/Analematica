# CLASIFICACIÓN Y ELIMINACIÓN DE AGENTES INFORMATIVOS — SARITA 2026

## 🎯 Objetivo (Bloque 15)
Erradicar la "Inutilidad Operativa". Queda terminantemente prohibido el despliegue de agentes que solo generen texto (Mocks) sin impacto en el estado persistente o financiero del sistema.

## 📋 Matriz de Clasificación Obligatoria

Cada clase de agente debe declarar su `tipo_agente` según esta taxonomía:

| Tipo | Propósito | Regla de Oro |
| :--- | :--- | :--- |
| **Ejecutivo** | Modificar estado ORM (Registro, Pago). | Debe usar `transaction.atomic()`. |
| **Estratégico** | Generar propuestas en `DecisionProposal`.| Debe disparar evaluación de riesgo. |
| **Correctivo** | Reversar o ajustar discrepancias. | Debe emitir evento de reversión. |
| **Informativo** | Solo reportar datos o generar texto. | **PROHIBIDO** (Convertir a N5). |

## 🛠️ Plan de Erradicación (Cierre Técnico)

1.  **Auditoría AST:** Identificar soldados N6 que no posean el método `perform_atomic_action` o que este retorne solo strings de texto.
2.  **Elevación de Rango:** Agentes que solo analicen datos (ej: `SoldadoCalculadorAmortizacion`) deben ser promovidos a la capa **N5 (Sargentos)** como servicios analíticos de soporte, liberando la capa N6 exclusivamente para la ejecución.
3.  **Hard Lock CI/CD:** El build de producción fallará si se detecta un agente de tipo `INFORMATIVO` en el registro del orquestador.

---
**Resultado:** Cada bit de procesamiento IA se traduce en una mutación real de la base de datos empresarial.
