# FLUJO OPERACIONAL FISCAL MULTI-DOMINIO — SARITA 2026

## 🎯 Objetivo (Bloque 5)
Implementar el cálculo automático de impuestos en todos los puntos de contacto económico del sistema, asegurando que la fiscalidad sea transversal y transparente.

## 🚀 Impacto por Dominio

### 📈 5.1 Ventas (Comercial)
- **Acción:** Confirmación de factura.
- **Impacto:** Cálculo de **IVA Generado** e **Impuesto al Consumo** según la categoría del producto y ubicación del cliente.
- **Resultado:** Desglose fiscal en el PDF de la factura y asiento contable automático.

### 👥 5.3 Nómina (Laboral)
- **Acción:** Liquidación de periodo.
- **Impacto:** Cálculo de **Retención en la Fuente** por salarios, **Aportes Patronales** y **Parafiscales**.
- **Resultado:** Registro de la obligación fiscal en el pasivo (Cuenta 2) y el gasto salarial.

### 📦 5.4 Inventario (Bodega)
- **Acción:** Recepción de mercancía.
- **Impacto:** Validación de **IVA Descontable**. Determinación de si el impuesto es un mayor valor del costo o un crédito fiscal.
- **Resultado:** Valoración correcta del activo en el Kardex y Ledger.

## ⚖️ Determinismo de Cálculo
Todo cálculo se basa en la **Tríada Fiscal**:
1.  `Jurisdiction` (País/Estado)
2.  `TaxClassification` (Régimen del Vendedor/Comprador)
3.  `EffectiveDate` (Versión de la tasa al momento del documento)

---
**Resultado:** Sarita es un sistema fiscalmente inteligente que previene errores humanos en la liquidación de impuestos.
