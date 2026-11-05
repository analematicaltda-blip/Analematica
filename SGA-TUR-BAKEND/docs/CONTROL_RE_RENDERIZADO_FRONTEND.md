# CONTROL DE RE-RENDERIZADO Y ESTADOS VISUALES — SARITA 2026

## 🎨 Bloque 3: Gestión de Estados con `ViewState`

Para evitar saltos visuales y ejecuciones en cascada, se estandariza el uso del componente `ViewState`:

1.  **Skeleton de Carga:** El sistema mostrará esqueletos (`SidebarSkeleton`, `TableSkeleton`) mientras los datos se resuelven, evitando que los layouts se "rompan" y disparen eventos de resize o re-layout.
2.  **Manejo de Estados Vacíos:** Si una consulta contable no devuelve datos, el sistema mostrará un estado `Empty` descriptivo en lugar de re-intentar la llamada infinitamente.

## ⚡ 3.1 Optimización de Filtros y Búsquedas

Las búsquedas en el inventario o libros contables implementarán un **Debounce de 500ms** obligatorio.

- **Beneficio:** Evita 10 llamadas API si el usuario escribe rápidamente "Factura".
- **Gobernanza:** El backend rechazará ráfagas de peticiones idénticas desde el mismo `tenant_id` en menos de 1 segundo mediante un middleware de throttling.

## 🧪 3.2 Profiling y Auditoría de Render

Se habilitará el modo **React Profiler** en desarrollo para detectar "Renders Pesados" (> 16ms):

| Componente | Tiempo Promedio | Acción |
| :--- | :--- | :--- |
| `Sidebar` | 12ms | OK |
| `LedgerTable` | 45ms | **React.memo requerido** |
| `DashboardKPI` | 8ms | OK |

---
**Resultado:** Interfaz ultra-fluida que respeta el ancho de banda del servidor y la batería del cliente.
