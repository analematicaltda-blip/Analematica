# ARQUITECTURA DEL MOTOR FISCAL (TAX ENGINE) — SARITA 2026

## 🎯 Objetivo (Bloque 3)
Establecer un motor centralizado, desacoplado y determinístico que orqueste todos los cálculos de impuestos del sistema. El `TaxEngine` es la única autoridad fiscal del ERP.

## 🏗️ Modelos de Datos Obligatorios (Bloque 4)

### 1. Definición de Impuesto (`Tax`)
| Campo | Tipo | Propósito |
| :--- | :--- | :--- |
| `code` | Char(20) | Identificador único (ej: `IVA-CO-19`). |
| `tax_type` | Enum | VAT, WITHHOLDING, CONSUMPTION, LABOR. |
| `jurisdiction`| FK | Vínculo con País/Estado. |
| `rate` | Decimal | Tasa aplicable (ej: `0.1900`). |
| `deductible` | Boolean | Si permite crédito fiscal (IVA Descontable). |

### 2. Reglas de Aplicación (`TaxRule`)
| Campo | Tipo | Propósito |
| :--- | :--- | :--- |
| `doc_type` | String | Factura, Nómina, Recibo. |
| `entity_type` | String | Régimen Común, Gran Contribuyente. |
| `min_base` | Decimal | Monto mínimo para aplicar (Base). |
| `condition` | String | Expresión lógica (ej: `total > 10000`). |

### 3. Evidencia Fiscal (`TaxTransaction`)
| Campo | Tipo | Propósito |
| :--- | :--- | :--- |
| `document_id` | UUID | Vínculo con el documento origen. |
| `base_amount` | Decimal | Monto sobre el cual se calculó. |
| `tax_amount` | Decimal | Impuesto resultante. |
| `integrity_hash`| Char(64) | Sello SHA-256 del cálculo. |

---
**Regla de Cierre:** Se prohíbe el uso de constantes de impuestos (`const IVA = 0.19`) en el código de ventas o nómina. Todo cálculo debe pasar por el `TaxEngine.calculate(payload)`.
