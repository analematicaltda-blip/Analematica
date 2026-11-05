# REPORTES Y DECLARACIONES FISCALES — SARITA 2026

## 🎯 Objetivo (Bloque 9)
Generar la evidencia necesaria para el cumplimiento tributario sin necesidad de intervención manual o hojas de cálculo externas.

## 📊 Módulos de Reporting

### 1. Libro de IVA (Débito vs Crédito)
- **Función:** Agrupar todas las `TaxTransactions` de tipo VAT.
- **Campos:** Documento Origen, CUFE, Base, Tasa, Monto Impuesto, Tercero (NIT).
- **Drill-down:** Posibilidad de abrir la factura original desde el reporte.

### 2. Certificados de Retención
- **Función:** Generar el acumulado de retenciones practicadas por el Tenant.
- **Resultado:** Archivo estructurado para reporte de información exógena.

### 3. Consolidado Holding (Estrategia Fiscal)
- **Función:** Sumar las obligaciones fiscales de todas las subsidiarias en un solo panel.
- **KPI:** `EffectiveTaxRate` (Tasa efectiva de impuestos del grupo).

## 🔒 Auditoría y Versionamiento (Bloque 7)
- **Tasa Histórica:** El reporte mostrará la tasa aplicada al momento del documento (ej: 19%), incluso si la ley cambia posteriormente al 21%.
- **Inmutabilidad:** Ningún reporte fiscal puede ser modificado manualmente. Cualquier ajuste debe ser mediante un asiento de corrección con firma del contador.

---
**Resultado:** Cierre fiscal masivo en minutos, con trazabilidad 100% auditable.
