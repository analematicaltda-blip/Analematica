# MOTOR DE CIERRE FISCAL (CLOSURE ENGINE) — SARITA 2026

## 🎯 Objetivo (Bloque 6 y 8)
Automatizar las validaciones de integridad y la generación del snapshot criptográfico antes de marcar un periodo como `CLOSED`. El cierre no es solo un cambio de estado, es la cristalización de la verdad financiera.

## 🛑 1. Validaciones Previas (Hard Check)

El motor rechazará el cierre si alguna de estas condiciones falla:
1.  **Balance de Prueba:** `abs(Total_Debito - Total_Credito) < 0.001`.
2.  **Conciliación Bancaria:** Todas las transacciones del Monedero Soberano deben estar en estado `RECONCILED`.
3.  **Integridad Fiscal:** No deben existir transacciones sin su correspondiente `TaxTransaction` (impuesto calculado).
4.  **Flujo Operativo:** Ninguna `FacturaVenta` o `PlanillaNomina` puede estar en estado `DRAFT` o `PENDING`.
5.  **Periodo Anterior:** El periodo `M-1` debe estar en estado `CLOSED` o `LOCKED`.

## ✍️ 2. Sello Criptográfico (Accounting Snapshot)

Al aprobarse las validaciones, el motor ejecutará:

1.  **Generación de JSON:** Un resumen estructurado que contiene:
    - Balances finales por cuenta.
    - Resumen de IVA y Retenciones.
    - Conteo de asientos procesados.
2.  **Cálculo de Hash SHA-256:** `closure_hash = SHA256(snapshot_json + prev_period_hash)`.
3.  **Firma Digital:** Se sella el hash con la **Clave Privada del Holding**, garantizando que el reporte es oficial e inalterable.

---
**Garantía:** Un periodo cerrado con este motor posee validez legal ante cualquier autoridad tributaria (DIAN/AFIP/SAT).
