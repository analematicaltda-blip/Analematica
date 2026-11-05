# CORRECCIÓN ESTRUCTURAL: ELIMINACIÓN DE BUCLES INFINITOS — SARITA 2026

## 📜 Propósito (Fase 2)
Estabilizar el ciclo de renderizado del frontend mediante la gestión estricta de dependencias y la memoización de funciones de fetching.

## 🛠️ 2.1 Estabilización del `AuthContext`

Para evitar el loop de "Verificación de Acceso", se implementará:
1.  **Short-circuit:** Si `user` ya está cargado, el efecto de inicialización no debe dispararse.
2.  **Manejo de Errores Silencioso:** Si `fetchUserData` falla por red (no por 401), se debe mantener el estado actual y no forzar `logout()`.

```typescript
// Refactor propuesto
useEffect(() => {
  if (token && !user) {
    fetchUserData();
  }
}, [token, user, fetchUserData]);
```

## 🧠 2.2 Memoización de Servicios y Hooks

### `useCallback` en Fetching:
Todas las funciones que disparan llamadas API (ej: `fetchData` en `useApi.ts`) deben estar envueltas en `useCallback` para mantener una referencia estable.

### `useMemo` en Configuraciones:
Las estructuras de navegación (como las del `Sidebar.tsx`) y los mapeos de permisos deben ser memoizados para evitar que el cambio en un estado menor (ej: abrir un colapsable) re-evalúe toda la jerarquía de roles.

## 🧹 2.3 Protocolo de Cleanup (Limpieza)

Todo componente que inicie un proceso asíncrono o una suscripción debe retornar su función de limpieza:

```typescript
useEffect(() => {
  let isMounted = true;

  const load = async () => {
    const data = await api.get('/...');
    if (isMounted) setData(data);
  };

  load();
  return () => { isMounted = false; };
}, [dependency]);
```

---
**Resultado:** Cero disparos innecesarios de llamadas API y estabilidad visual absoluta en el Dashboard.
