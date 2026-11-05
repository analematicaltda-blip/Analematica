# OPTIMIZACIÓN Y EXPOSICIÓN FRONTEND — SARITA 2026

## 🚀 Bloque 8: Optimización de Producción

Para garantizar un Dashboard fluido con alto volumen de datos, la API Contable implementa:

1.  **Paginación Cursor-Based:** Listados de asientos (`/asientos`) no devuelven miles de filas; usan cursores para navegación rápida.
2.  **Agregaciones Preprocesadas:** Los totales del Balance General se consultan desde la tabla `ConsolidatedSnapshot` si el periodo está cerrado, evitando cálculos costosos en tiempo real.
3.  **Compresión Gzip/Brotli:** Activa para todas las respuestas JSON de reportes, reduciendo el consumo de ancho de banda del prestador.

## 🔗 Bloque 11: Integración de Hooks React

Se actualiza el `useMiNegocioApi.ts` para centralizar las llamadas:

```typescript
export const useAccountingHub = () => {
  const getBalance = (date: string) =>
      api.get(`/api/contabilidad/balance?date=${date}`);

  const getAsientos = (page: number) =>
      api.get(`/api/contabilidad/asientos?page=${page}`);

  const reverseAsiento = (id: string, reason: string) =>
      api.post(`/api/contabilidad/reverse/${id}/`, { reason });

  return { getBalance, getAsientos, reverseAsiento };
};
```

---
**Resultado:** El frontend se convierte en un visor profesional de datos financieros determinísticos.
