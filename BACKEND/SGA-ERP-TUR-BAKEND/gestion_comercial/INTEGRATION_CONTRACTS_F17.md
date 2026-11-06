# Auditoría de Integración y Contratos Explícitos – FASE 17
## Módulo: `gestion_comercial`

Este documento audita y formaliza las integraciones existentes entre `gestion_comercial` y el resto del ecosistema de "Mi Negocio", siguiendo los principios de la Fase 17.

---

### 1. Lista de Sistemas Consumidores/Proveedores Identificados

`gestion_comercial` no expone datos para ser consumidos pasivamente por otros sistemas. En cambio, **actúa como un sistema iniciador** que invoca activamente a otros módulos durante sus transacciones.

Las integraciones identificadas son:

1.  **`gestion_contable`**: Invocado durante la creación de una factura y el registro de un pago.
2.  **`gestion_financiera`**: Invocado durante el registro de un pago.
3.  **`gestion_operativa`**: Actúa como proveedor de datos maestros (Clientes, Productos, Perfil).

---

### 2. Definición de Contratos de Integración Existentes

#### Integración 1: Creación de Factura → Contabilidad

*   **Propósito:** Registrar el impacto contable de una nueva venta.
*   **Mecanismo:** Llamada directa a los modelos de `gestion_comercial` desde `gestion_contable.contabilidad` dentro de una transacción atómica (`transaction.atomic`) en el `FacturaVentaViewSet`.
*   **Contrato (Implícito, ahora documentado):**
    *   **Endpoint Consumidor:** No aplica (es una llamada interna).
    *   **Endpoint Expuesto:** `POST /api/v1/mi-negocio/comercial/facturas-venta/`
    *   **Tipo de Relación:** Escritura (`gestion_comercial` escribe en `gestion_contable`).
    *   **Reglas de Negocio:**
        1.  Toda `FacturaVenta` creada **debe** generar un `JournalEntry` (Asiento Contable).
        2.  El `JournalEntry` debe tener dos `Transaction` (Transacciones Contables): un débito a Cuentas por Cobrar (`1305`) y un crédito a Ingresos (`4135`).
        3.  El monto de las transacciones debe ser igual al `total` de la `FacturaVenta`.
    *   **Riesgo de Acoplamiento (Identificado):** **Alto.** La lógica de negocio está acoplada estructuralmente. `gestion_comercial` conoce la implementación interna de los modelos de `gestion_contable`.
    *   **Validación de Impacto Cruzado:** El uso de `transaction.atomic` es el mecanismo clave que garantiza la integridad. Si la creación del `JournalEntry` falla, toda la creación de la `FacturaVenta` se revierte. Esto previene la corrupción de datos y cumple con la directriz de que una caída en un sistema no debe corromper al otro.

#### Integración 2: Registro de Pago → Contabilidad y Tesorería

*   **Propósito:** Registrar la entrada de dinero en tesorería y saldar la cuenta por cobrar en contabilidad.
*   **Mecanismo:** Llamada directa a modelos de `gestion_financiera` y `gestion_contable` dentro de la acción `registrar-pago` del `FacturaVentaViewSet`, protegida por `transaction.atomic`.
*   **Contrato (Implícito, ahora documentado):**
    *   **Endpoint Consumidor:** No aplica.
    *   **Endpoint Expuesto:** `POST /api/v1/mi-negocio/comercial/facturas-venta/{id}/registrar-pago/`
    *   **Tipo de Relación:** Escritura (`gestion_comercial` escribe en `gestion_financiera` y `gestion_contable`).
    *   **Reglas de Negocio:**
        1.  Un pago **debe** crear una `TransaccionBancaria` (Tesorería) de tipo `INGRESO`.
        2.  Un pago **debe** crear un `JournalEntry` (Contabilidad) que salde la cuenta por cobrar.
        3.  El `JournalEntry` debe debitar la cuenta de Caja/Bancos y acreditar la de Cuentas por Cobrar (`130505`).
    *   **Riesgo de Acoplamiento (Identificado):** **Alto.** Mismo acoplamiento estructural que en la creación de la factura.
    *   **Validación de Impacto Cruzado:** Protegido igualmente por `transaction.atomic`. Un fallo en cualquiera de los módulos revierte toda la operación.

---

### 3. Conclusión de la Auditoría

*   **Principio de Frontera Dura:** **NO SE CUMPLE.** El módulo `gestion_comercial` viola este principio al importar y manipular directamente los modelos de otros módulos. Esto representa la principal fuente de deuda técnica y riesgo de acoplamiento.
*   **Aislamiento:** Aunque no hay dependencias de módulos no relacionados, el fuerte acoplamiento con `contabilidad` y `financiera` impide que `gestion_comercial` sea verdaderamente autónomo.
*   **Sugerencia (Fuera de Alcance de Fase 17):** Una futura refactorización debería desacoplar esta lógica, posiblemente a través de un sistema de señales de Django o un bus de eventos, donde `gestion_comercial` simplemente emita un evento `factura_creada` y los otros módulos reaccionen a él.

Este documento formaliza el estado actual de las integraciones, sus riesgos y sus mecanismos de protección, cumpliendo con el objetivo de auditoría y documentación de la Fase 17.
