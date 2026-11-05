# Gobierno del Dominio y Evolución Controlada – FASE 18
## Módulo: `gestion_comercial`

Este documento establece las reglas, límites y criterios técnicos permanentes que gobiernan el dominio de `gestion_comercial`. Su propósito es asegurar que la evolución del módulo sea predecible y que su diseño resista futuras demandas operativas sin degradarse.

---

### 1. Declaración Oficial del Dominio

#### Qué **SÍ** es `gestion_comercial`:
El dominio de `gestion_comercial` es responsable exclusivamente del **ciclo de vida de la venta y la facturación**. Esto incluye:
- **Facturación:** Crear, leer, actualizar, anular y gestionar el estado de las facturas de venta.
- **Ítems Comercializables:** Definir los ítems de línea dentro de una factura, incluyendo descripción, cantidad y precio.
- **Reglas de Precios:** Gestionar el precio unitario y los cálculos de subtotales por línea.
- **Reglas de Impuestos y Totales:** Actuar como la **única fuente de verdad** para el cálculo de impuestos y totales de una factura.
- **Clientes (como consumidores):** Gestionar la relación entre una factura y un cliente. El maestro de clientes reside en `gestion_operativa`.
- **Registro de Pagos:** Iniciar el flujo de registro de un pago contra una factura, que luego se delega a los dominios de finanzas y contabilidad.

#### Qué **NO** es `gestion_comercial`:
Este módulo **NO DEBE** implementar lógica de negocio que pertenezca a otros dominios, aunque esté relacionada. Se prohíbe explícitamente:
- **Gestión de Inventarios:** No controla stock, almacenes ni movimientos de inventario. Solo consume un "Producto" como ítem vendible.
- **Contabilidad Profunda:** No gestiona planes de cuentas, libros mayores ni estados financieros. Solo **inicia** la creación de asientos contables.
- **Tesorería y Flujo de Caja:** No gestiona cuentas bancarias, conciliaciones ni flujo de efectivo. Solo **inicia** el registro de una transacción de ingreso.
- **Gestión de Operación Turística:** No maneja reservas, disponibilidad, calendarios ni logística.
- **Nómina o RRHH:** No tiene ninguna relación con empleados o pagos de personal.
- **Reportería Global:** No genera reportes consolidados del negocio. Su reportería se limita a su propio dominio (ej. listado de facturas).

---

### 2. Catálogo de Reglas de Negocio

#### Reglas Duras (No Negociables)
1.  **Backend es la Única Fuente de Verdad:** Todos los cálculos monetarios (subtotales, impuestos, totales) y la gestión de estados son responsabilidad exclusiva del backend. El frontend es una capa de presentación pura.
2.  **Inmutabilidad de Estados Finales:** Una factura en estado `PAGADA` o `ANULADA` no puede ser modificada bajo ninguna circunstancia.
3.  **Integridad Transaccional:** Toda operación que afecte a múltiples dominios (ej. crear factura y su asiento contable) debe ser atómica. Si una parte falla, todo se revierte (`transaction.atomic`). No existen operaciones a medias.
4.  **Propiedad de los Datos:** Todos los registros de `gestion_comercial` deben estar asociados a un `ProviderProfile` (tenant). No existen datos globales.

#### Supuestos Explícitos del Negocio
1.  **Tasa de Impuestos Fija:** Actualmente, el sistema asume una tasa de impuestos única y fija (19%), definida en el backend. Una futura evolución podría requerir que esta tasa sea configurable.
2.  **Modelo de Cliente Simplificado:** Se asume que los datos del modelo `Cliente` de `gestion_operativa` son suficientes para la facturación.

---

### 3. Política de Cambio del Dominio

Todo cambio o nueva funcionalidad propuesta para `gestion_comercial` debe ser documentado en un Pull Request siguiendo este protocolo:

1.  **Justificación del Cambio:** ¿Por qué es necesario este cambio? ¿Qué problema de negocio resuelve?
2.  **Alineación con el Dominio:** ¿Cómo encaja este cambio en la "Declaración Oficial del Dominio"?
3.  **Impacto en Integraciones:** ¿Afecta a `gestion_contable` o `gestion_financiera`? ¿Cómo se manejará el cambio en esos módulos?
4.  **Riesgo de Regresión:** ¿Qué funcionalidades existentes podrían verse afectadas? ¿Cómo se probará?
5.  **Pruebas Mínimas:** El cambio debe venir acompañado de al menos una prueba unitaria o de API que valide su comportamiento.

**Los cambios que no cumplan con este protocolo serán rechazados.**

---

### 4. Lista de Deuda Técnica Consciente

1.  **Acoplamiento Estructural con `contabilidad` y `financiera`:**
    *   **Decisión Consciente:** Se aceptó el acoplamiento directo (importar y usar modelos de otros módulos) para acelerar la entrega de valor y garantizar la integridad de los datos a través de `transaction.atomic`.
    *   **Riesgo:** Un cambio en los modelos de `gestion_contable` puede romper `gestion_comercial`.
    *   **Refactor Pendiente (Largo Plazo):** Implementar un sistema de señales (Signals) o un bus de eventos para desacoplar los módulos. `gestion_comercial` emitiría un evento como `factura_creada`, y los otros módulos se suscribirían para reaccionar a él.

2.  **Código Desactivado (`_obsoleto_`):**
    *   **Justificación:** Se desactivaron módulos y pruebas antiguas que no se alineaban con la nueva arquitectura para estabilizar el sistema rápidamente.
    *   **Riesgo:** Mínimo, ya que una auditoría confirmó que no hay referencias activas a este código.
    *   **Acción Pendiente:** Eliminar permanentemente estos directorios una vez que el sistema demuestre estabilidad a largo plazo.
