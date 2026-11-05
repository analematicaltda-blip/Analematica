# Arquitectura y Flujo del Pipeline de Facturación – FASE 19

Este documento define la arquitectura desacoplada para el proceso de facturación, separando las responsabilidades entre los dominios Comercial, Contable y Fiscal.

---

### 1. Diagrama de Flujo y Responsabilidades

El flujo sigue un pipeline unidireccional donde cada módulo enriquece y transforma los datos del anterior, sin acoplamiento estructural.

```
[gestion_comercial] ----(Evento: FacturaComercialConfirmada)----> [facturacion] ----(Solicitud API)----> [facturacion_electronica]
       |                                                            |                                       |
       |                                                            |                                       |
  - Intención de Venta                                         - Documento Contable Interno          - Documento Legal (DIAN)
  - Pre-cálculo de totales                                     - Validación de reglas contables      - Generación de CUFE/QR
  - Estado: BORRADOR                                           - Cálculo de impuestos finales        - Firma digital
  - Estado: COMERCIAL_CONFIRMADA                               - Numeración de resolución interna    - Envío a la DIAN
                                                               - Estado: CONTABLE_APROBADA           - Consulta de estado DIAN
```

#### **Separación Contractual Obligatoria:**

| Módulo                  | Responsabilidad Principal                                     |
| ----------------------- | ------------------------------------------------------------- |
| `gestion_comercial`     | Gestionar la **intención de venta** y el acuerdo con el cliente. |
| `facturacion`           | Crear el **documento contable interno** y validar reglas de negocio. |
| `facturacion_electronica` | Generar y gestionar el **documento legal** ante la DIAN. |

**Regla de Oro:** `gestion_comercial` orquesta el inicio del flujo, pero **no tiene autoridad fiscal ni contable.**

---

### 2. Contrato de Salida de `gestion_comercial`

Cuando una `FacturaVenta` pasa al estado `COMERCIAL_CONFIRMADA`, se emite un evento (`FacturaComercialConfirmada`) con el siguiente payload. Este es el **único contrato de integración autorizado** que `gestion_comercial` expone.

**Evento:** `FacturaComercialConfirmada`

**Payload (Contrato de Salida V1):**
```json
{
  "id_factura_comercial": "UUID de la FacturaVenta",
  "perfil_id": "ID del ProviderProfile (tenant)",
  "usuario_id": "ID del usuario que confirma",
  "fecha_confirmacion": "Timestamp de la confirmación",
  "cliente": {
    "id": "ID del Cliente",
    "nombre": "Nombre del Cliente",
    "email": "Email del Cliente"
  },
  "items": [
    {
      "producto_id": "UUID del Product",
      "descripcion": "Descripción del ítem en la factura",
      "cantidad": "Decimal",
      "precio_unitario": "Decimal"
    }
    // ... más ítems
  ],
  "moneda": "COP" // Asumido por ahora, podría ser dinámico
}
```

**Campos Explícitamente Excluidos:**
Los siguientes campos **NO** forman parte del contrato de salida, ya que son responsabilidad de los módulos posteriores:
- `impuestos`
- `totales_finales`
- `CUFE` / `QR`
- `resolucion_dian`
- `numeracion_legal`

---

### 3. Trazabilidad Completa

La trazabilidad se garantiza mediante el encadenamiento de IDs a través de los módulos.
- El módulo `facturacion` debe almacenar `id_factura_comercial` en su modelo de `FacturaContable`.
- El módulo `facturacion_electronica` debe almacenar `id_factura_contable` en su modelo de `FacturaElectronica`.

Esto permite reconstruir la historia completa de una transacción desde su origen comercial hasta su estado final en la DIAN.
