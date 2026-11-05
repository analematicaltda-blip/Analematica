# PLAN DE CUENTAS CORPORATIVO (PCC) — SARITA 2026

## 🎯 Objetivo (Bloque 5)
Normalizar la información financiera de todas las filiales mediante un Plan de Cuentas Maestro. Esto permite comparar "peras con peras" independientemente de la normativa local (Local GAAP) de cada país.

## 🏗️ Estructura del PCC (IFRS Homologado)

| Nivel | Código | Nombre | Propósito |
| :--- | :--- | :--- | :--- |
| **1** | `1.0.0` | **Activo** | Recursos controlados por el grupo. |
| **2** | `1.1.0` | **Activo Corriente**| Liquidez inmediata. |
| **3** | `1.1.1` | **Efectivo y Equiv.**| Caja, Bancos, Monedero Digital. |
| **4** | `1.1.1.01`| **Caja General** | Dinero físico en sucursales. |

## 🔄 Tabla de Homologación (Mapeo Local -> PCC)

Cada Tenant debe configurar su mapeo obligatorio en el modelo `Account.consolidation_mapping`:

| Empresa | Cuenta Local | PCC | Descripción |
| :--- | :--- | :--- | :--- |
| **Hotel A (COL)** | `110505` (Caja) | `1.1.1.01` | Mapeo directo a Caja General. |
| **Agencia B (USA)**| `1010` (Cash) | `1.1.1.01` | Mapeo a estándar corporativo. |
| **Holding (GLOBAL)**| `2205` (Prov.) | `2.1.5.01` | Mapeo de Pasivos Corrientes. |

## 📝 Reglas de Normalización

1.  **Mapeo 1:N:** Una cuenta del PCC puede recibir saldos de múltiples cuentas locales.
2.  **Validación de Mapeo:** El sistema bloqueará la consolidación si existe una cuenta local con saldo != 0 que no tenga un código PCC asignado.
3.  **Inmutabilidad:** El PCC solo puede ser modificado por el **CFO Holding** mediante aprobación del `GovernanceKernel`.

---
**Resultado:** Visibilidad unificada del balance del grupo al segundo, sin importar la moneda o el país de origen.
