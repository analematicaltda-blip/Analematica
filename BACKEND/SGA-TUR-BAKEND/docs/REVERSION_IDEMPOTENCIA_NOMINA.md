# REVERSIÓN E IDEMPOTENCIA LABORAL — SARITA 2026

## 🆔 Bloque VII: Idempotencia de Nómina
Para evitar que una nómina se contabilice dos veces por reintentos asíncronos, el sistema implementará una **Clave Compuesta** en la tabla `idempotency_keys`:

`key = MD5(nominaId + version + tenantId)`

**Lógica Inviolable:** Si un evento con la misma clave llega al dominio contable y ya tiene un `status = SUCCESS`, el soldado devuelve el `asientoId` existente sin procesar nada.

## ↩️ Bloque VIII: Reversión Controlada
Si una nómina es anulada comercialmente (ej: error en liquidación detectado post-cierre), se sigue este protocolo inmutable:

1.  **Evento:** Nómina emite `NominaAnulada`.
2.  **Búsqueda:** El dominio contable localiza el `asientoId` original vinculado a la `nominaId`.
3.  **Acción:** El soldado genera un **Asiento Espejo Inverso**:
    - Lo que era Débito pasa a Crédito.
    - Lo que era Crédito pasa a Débito.
4.  **Marca:** El asiento original se marca como `reverted_at = NOW()`.
5.  **Notificación:** Emisión de `AsientoNominaRevertido`.

---
**Prohibición:** Queda terminantemente prohibido el uso de `DELETE` sobre asientos contables generados por nómina. Toda corrección debe dejar huella en los libros.
