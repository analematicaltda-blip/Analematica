# MATRIZ DE OPERATIVIDAD Y CERTIFICACIÓN — SARITA 2026

## 📊 Bloque 6: SoldadoOperationalStatus (Tabla de Madurez)

El sistema mantendrá una tabla viva de certificación técnica por soldado:

| Soldado | Dominio | Persistente | EventBus | Idempotente | Status Final |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `RegistroIngreso` | CONTABLE | ✅ | ✅ | ✅ | **READY** |
| `Incidentes` | SST | ✅ | ✅ | ✅ | **READY** |
| `Prestaciones` | NÓMINA | ❌ | ⚠️ | ❌ | **BLOCKED** |

**Regla de Deploy:** Si un soldado en el árbol de dependencias de la misión tiene status `BLOCKED`, el orquestador aborta la operación completa.

## 🧪 Bloque 8: Test de Integración Global (Escenarios Reales)

Antes del cierre absoluto, se deben validar estos flujos "End-to-End":

1.  **Flujo Comercial:** Venta -> Emisión Factura -> Registro Ingreso (N6) -> Actualización Saldo Wallet.
2.  **Flujo Laboral:** Registro Novedad (N6) -> Liquidación Nómina (N6) -> Generación Asiento Gasto.
3.  **Flujo Financiero:** Registro Crédito (N6) -> Generación Amortización -> Causación de Intereses (N6).

## 🔒 Bloque 9: Hard Lock de Producción

Se implementará un "System Maturity Gate" en el CI/CD:
```bash
if (check_soldier_mocks() > 0) OR (test_coverage < 85%):
    raise DeploymentBlocked("El sistema posee piezas no operacionales.")
```

---
**Declaratoria (Bloque 10):** El sistema Sarita alcanzará el estado de **"100% Operacional Integrado"** solo cuando el total de la matriz de operatividad sea **READY**.
