# INFORME DE AUDITORÍA Y PLAN DE PERFECCIONAMIENTO: MÓDULO CONTABLE ERP (GATURISTICA)
**Referencia Técnica:** Auditoría frente a suites `Conta-Skills` (`gestor-autonomos`) y `skills-contabilidad` (`month-end-close`, `profit-loss`, `bank-sync`, `tax-prep`, `smart-split`).
**Estado:** Directriz de Implementación y Arquitectura Aprobada.

---

## I. DIAGNÓSTICO DE INCONSISTENCIAS Y BRECHAS IDENTIFICADAS

### 1. Ausencia de Endpoints Expuestos para Asientos Contables (`JournalEntry`) y Períodos
- **Hallazgo:** En `GATuristica/SGA-ERP-TUR-BAKEND/gestion_contable/contabilidad/urls.py`, el `DefaultRouter` únicamente registra `PlanCuentaViewSet` (`/cuentas`).
- **Inconsistencia:** No existen rutas registradas para `/asientos/` ni `/periodos/`, a pesar de que los modelos proxy `AsientoContable`, `Transaccion` y `PeriodoContable` ya están definidos en `models.py`. La ruta documentada en la directriz (`/api/v1/mi-negocio/contable/asientos/`) requiere su router oficial activo.
- **Impacto:** Las vistas frontend de `asientos/nuevo` y los agentes autónomos de contabilización no pueden consultar ni persistir partidas dobles de forma estándar vía API REST.

### 2. Motor de Conciliación Bancaria y Pasarelas de Pago Automatizado
- **Comparativa con `skills-contabilidad/shared/bank-sync` y `Conta-Skills/procesar_stripe.py`:**
- **Hallazgo:** En el backend del ERP existe lógica aislada de transacciones, pero no cuenta con un motor de coincidencia determinístico (*deterministic matching engine*) basado en:
  - Tolerancia de fechas (ventana de +/- 3 días).
  - Reglas difusas por descripción / referencia de transacción.
  - Conciliación de comisiones de intermediación y pasarelas de pago (Stripe, Monedero, datáfono).
- **Impacto:** La conciliación en `tesoreria/conciliacion-wallet` requiere intervención manual y no previene duplicados.

### 3. Pipeline Integral de Cierre Mensual y Checklist Fiscal (`month-end-close` & `tax-prep`)
- **Hallazgo:** `GATuristica/SGA-ERP-TUR-BAKEND/gestion_contable/cierres/services.py` solo efectúa una verificación básica de balance (`sum(debits) == sum(credits)`).
- **Brechas según las Skills:**
  - Falta cálculo y asiento automático de depreciación acumulada mensual de activos fijos (`depreciation-schedule`).
  - Falta provisión y liquidación periódica de impuestos directos e indirectos (IVA generado vs descontable, Retención en la Fuente, ICA municipal) como estipula `Conta-Skills/calcular_iva.py` y `calcular_irpf.py`.
  - Falta bloqueo estricto e inmutabilidad del período contable (`FiscalPeriod.is_closed = True`) con trazabilidad de hash encadenado.

### 4. Integración Reactiva Bidireccional entre Reservas/Servicios y Devengo Contable
- **Hallazgo:** En `GATuristica/SGA-ERP-TUR-FRONTEND/reservas/page.tsx` y `servicios/page.tsx`, los contratos con `/api/v1/turismo/tourism-reservations/` y `/api/v1/turismo/tourism-services/` están declarados en la interfaz pero desconectados del ciclo de causación contable.
- **Solución:** Cada reserva confirmada en la plataforma turística debe emitir un evento que dispare el asiento de devengo (Débito a Cuentas por Cobrar 1305, Crédito a Ingresos por Servicios Turísticos 4140) bajo estricto aislamiento multi-inquilino.

---

## II. PLAN DE IMPLEMENTACIÓN TÉCNICA (HOJA DE RUTA)

### Fase 1: Exposición y Endpoints del Core Contable (Backend)
1. **Serializers:** Crear `AsientoContableSerializer`, `TransaccionSerializer` y `PeriodoContableSerializer` con validación estricta de partida doble (`sum(debit) == sum(credit)`).
2. **ViewSets:** Registrar `AsientoContableViewSet` y `PeriodoContableViewSet` en `contabilidad/views.py`.
3. **Enrutamiento:** Conectar en `GATuristica/SGA-ERP-TUR-BAKEND/gestion_contable/contabilidad/urls.py`:
   - `router.register(r'asientos', AsientoContableViewSet, basename='asiento-contable')`
   - `router.register(r'periodos', PeriodoContableViewSet, basename='periodo-contable')`

### Fase 2: Motor de Reglas Fiscales y Conciliación (Integración Skills)
1. **Reglas de Impuestos:** Adaptar la lógica de `Conta-Skills/skills/gestor-autonomos/scripts/calcular_iva.py` para la parametrización de tarifas colombianas (0%, 5%, 19%) y retenciones en la fuente.
2. **Bank Sync Engine:** Implementar el servicio `AutomatedBankReconciler` en `gestion_financiera/services/` inspirado en `skills-contabilidad/shared/bank-sync/SKILL.md`.
3. **Cierre Mensual:** Automatizar el checklist de `month-end-close` en `cierres/services.py` para generar el asiento de cierre contra la cuenta de pérdidas y ganancias (cuenta 5905).

### Fase 3: Gobernanza e Interfaz en Frontend
1. Mantener la separación de responsabilidades:
   - **GATuristica Admin:** Panel empresarial privado (contabilidad, nómina, POS, DIAN).
   - **Turismo Admin:** Panel territorial público (catálogo, prestadores, eventos).
2. Paleta cromática estandarizada: **Azul Metalizado** (`#1e3a8a`, `#0f172a`) y **Azul Claro** (`#38bdf8`, `#0284c7`, `#e0f2fe`).
