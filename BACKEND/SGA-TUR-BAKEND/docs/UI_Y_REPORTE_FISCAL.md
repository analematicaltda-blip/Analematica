# PANEL DE GESTIÓN FISCAL Y CERTIFICACIÓN — SARITA 2026

## 🖥️ Bloque 5: Interfaz Administrativa (UI)

El panel administrativo en `/dashboard/admin/fiscal` ofrecerá:

1.  **Línea de Tiempo Fiscal:** Listado de meses con semáforo de estado:
    - 🟢 `OPEN`: Botón [CERRAR].
    - 🔴 `CLOSED`: Botón [REABRIR] (Requiere firma CFO).
    - 🔒 `LOCKED`: Botón [VER REPORTE].
2.  **Dashboard de Pre-cierre:** Checklist dinámico que muestra asientos descuadrados o facturas en borrador que bloquean el cierre.

## 🧾 Bloque 13: Reporte de Auditoría Automático

Al cerrar un periodo, el sistema genera el archivo `CERT-FISCAL-[PERIOD].pdf`:

- **Contenido:**
    - Balance de Prueba Consolidado.
    - Resumen de Impuestos por Tipo (IVA/Retenciones).
    - Identificación del Responsable (Nombre y Cargo).
    - **Hash SHA-256 del Periodo:** Huella digital única.
    - **Código QR de Verificación:** Vínculo a la API de auditoría pública para validar la integridad del documento.

---
**Criterio de Éxito:** El sistema debe permitir descargar reportes certificados de cualquier mes pasado en menos de 5 segundos, garantizando la inmutabilidad de la información.
