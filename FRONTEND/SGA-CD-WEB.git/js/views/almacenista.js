// js/views/almacenista.js — Vista para el Rol de Almacenista (hereda de jefe_almacen.js)

if (typeof registerView === 'function') {
    registerView('almacenista', 'ver-inventario', renderDashboardInventarioView);
    registerView('almacenista', 'registrar-movimientos', renderRegistrarMovimientosView);
}
