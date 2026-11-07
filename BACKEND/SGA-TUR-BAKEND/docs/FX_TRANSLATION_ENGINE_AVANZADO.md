# FX TRANSLATION ENGINE AVANZADO — SARITA 2026

## 🎯 Objetivo (Bloque 21)
Soportar la consolidación multinacional mediante un motor de conversión multimoneda que cumpla con los estándares internacionales de auditoría (IFRS/IAS 21).

## 🏗️ 21.3 Arquitectura del Engine

### 1. FXRateProvider
- **Responsabilidad:** Conector único para la ingesta de tasas.
- **Fuentes:** Tasas oficiales (Bancos Centrales) registradas con firma digital.
- **Tipos de Tasa:**
    - `SPOT`: Valor del día (Reconocimiento inicial).
    - `MONTHLY_AVERAGE`: Promedio del periodo (Cuentas de Resultado).
    - `CLOSING`: Valor al día del reporte (Cuentas de Balance).

### 2. FXConversionService (Lógica Inviolable)
El servicio aplicará la tasa correcta automáticamente basándose en la naturaleza de la cuenta:
```python
def translate_line(amount, account_type, date):
    if account_type in ['ASSET', 'LIABILITY']:
        rate = FXRateStore.get_closing_rate(date)
    elif account_type in ['REVENUE', 'EXPENSE']:
        rate = FXRateStore.get_average_rate(date.month, date.year)
    else: # EQUITY
        rate = FXRateStore.get_historical_rate(date)
    return amount * rate
```

## 📝 21.5 Validaciones Técnicas
- **Cero Conversión Manual:** Prohibido inyectar tasas "ad-hoc" en los reportes consolidados.
- **Check de Redondeo:** El motor detectará discrepancias por decimales (Meta: < 0.001) y las llevará a la cuenta de **Diferencia por Conversión** en el Patrimonio.

---
**Resultado:** Balances consolidados 100% reproducibles y auditables por firmas internacionales.
