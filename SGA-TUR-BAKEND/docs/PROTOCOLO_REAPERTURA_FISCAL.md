# PROTOCOLO DE REAPERTURA GOBERNADA — SARITA 2026

## 🚨 Bloque 9: Reapertura de Periodos Cerrados

En cumplimiento con el principio de "Cuatro Ojos" (4-eyes principle), la reapertura de un periodo fiscal es una **Acción Crítica** que no puede ser realizada por un solo actor.

### 1. Requisitos Inviolables
- **Rol Autorizado:** Solo el `CFO` o el `SUPER_ADMIN`.
- **Aprobación Dual:** Requiere el sello digital de un segundo oficial de cumplimiento.
- **Justificación Legal:** Registro obligatorio del motivo (ej: "Ajuste por auditoría externa").

### 2. Ciclo de Reapertura
1.  **Solicitud:** El contador inicia la intención de reapertura.
2.  **Validación:** El sistema verifica que el periodo no esté en estado `LOCKED` (El estado `LOCKED` es irreversible).
3.  **Aprobación:** El CFO firma digitalmente la autorización.
4.  **Ejecución:** El periodo pasa a estado `REOPENED`.
5.  **Historial:** Se registra en la tabla `FiscalPeriodAudit` el `reopened_by`, `reopened_at` y el hash del estado anterior.

### 3. Restricción del estado `LOCKED`
Un periodo marcado como **LOCKED** (Normalmente tras la declaración oficial de impuestos anual) **NUNCA** puede volver a abrirse. Toda corrección debe realizarse en el periodo presente.

---
**Resultado:** Gobernanza absoluta sobre la integridad de los datos financieros históricos.
