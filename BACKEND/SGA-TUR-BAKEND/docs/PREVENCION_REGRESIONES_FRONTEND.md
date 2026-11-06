# PREVENCIÓN DE REGRESIONES Y QA FRONTEND — SARITA 2026

## 🛡️ Bloque 4: Reglas de Gobernanza en Código (Linting)

Para garantizar que el Bucle Infinito no regrese, se activan las siguientes reglas de **ESLint** de carácter obligatorio para el build de producción:

1.  **`react-hooks/exhaustive-deps` (Error):** Impide el deploy si un `useEffect` tiene dependencias incompletas o inestables.
2.  **`no-setstate-in-render`:** Bloquea actualizaciones de estado fuera de efectos o manejadores de eventos.
3.  **`no-new-object-in-jsx`:** Evita pasar literales `{}` o `[]` como props a componentes que usen `React.memo`.

## 🧪 Bloque 5: Validación de Integridad Operativa

Se auditaron los flujos financieros finales para asegurar que el frontend no provoque duplicidad:

- **Confirmación de Pago:** El botón de "Pagar" se desactiva inmediatamente tras el primer clic (`isSubmitting`).
- **Sincronización de Nómina:** Si el usuario pulsa "Liquidar", el sistema muestra un overlay bloqueante hasta que el `OutboxEvent` sea procesado por el backend, evitando el envío de múltiples misiones de liquidación.

## ✅ Declaratoria Final
Se confirma que el frontend de Sarita es ahora **Determinístico y Estable**. No existen bucles infinitos detectados en las rutas críticas de Vía 1, Vía 2 o Vía 3.

---
**Firmado:** Jules, Software Engineer Audit.
