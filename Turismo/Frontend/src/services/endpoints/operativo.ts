import httpClient from '../index';

export const operativoEndpoints = {
  getPerfil: () => httpClient.get('/v1/mi-negocio/operativa/perfil/me/'),
  updatePerfil: (data: any) => httpClient.patch('/v1/mi-negocio/operativa/perfil/update-me/', data),
  getClientes: () => httpClient.get('/v1/mi-negocio/operativa/clientes/'),
  getProductosServicios: () => httpClient.get('/v1/mi-negocio/operativa/productos-servicios/'),
  createProductoServicio: (data: any) => httpClient.post('/v1/mi-negocio/operativa/productos-servicios/', data),
  updateProductoServicio: (id: number, data: any) => httpClient.patch(`/v1/mi-negocio/operativa/productos-servicios/${id}/`, data),
  deleteProductoServicio: (id: number) => httpClient.delete(`/v1/mi-negocio/operativa/productos-servicios/${id}/`),
  getReservas: () => httpClient.get('/v1/mi-negocio/operativa/reservas/'),

  // SG-SST (Actualizado Fase 7)
  getSSTDashboard: () => httpClient.get('/v1/mi-negocio/operativa/sst/dashboard/'),
  getSSTRisks: () => httpClient.get('/v1/mi-negocio/operativa/sst/riesgos/'),
  getSSTIncidents: () => httpClient.get('/v1/mi-negocio/operativa/sst/incidentes/'),
  reportSSTIncident: (data: any) => httpClient.post('/v1/mi-negocio/operativa/sst/incidentes/', data),
  getSSTPlanAnual: () => httpClient.get('/v1/mi-negocio/operativa/sst/plan-anual/'),
  getSSTCapacitaciones: () => httpClient.get('/v1/mi-negocio/operativa/sst/capacitaciones/'),
  getSSTInspecciones: () => httpClient.get('/v1/mi-negocio/operativa/sst/inspecciones/'),
  getSSTIndicadores: () => httpClient.get('/v1/mi-negocio/operativa/sst/indicadores/'),
  getSSTAlertas: () => httpClient.get('/v1/mi-negocio/operativa/sst/alertas/'),

  getNomina: () => httpClient.get('/v1/mi-negocio/operativa/nomina/'),

  // Módulos Especializados
  getHotelRoomTypes: () => httpClient.get('/v1/mi-negocio/operativa/hotel/room-types/'),
  createHotelRoomType: (data: any) => httpClient.post('/v1/mi-negocio/operativa/hotel/room-types/', data),
  updateHotelRoomType: (id: number, data: any) => httpClient.patch(`/v1/mi-negocio/operativa/hotel/room-types/${id}/`, data),
  deleteHotelRoomType: (id: number) => httpClient.delete(`/v1/mi-negocio/operativa/hotel/room-types/${id}/`),

  getHotelRooms: () => httpClient.get('/v1/mi-negocio/operativa/hotel/rooms/'),
  createHotelRoom: (data: any) => httpClient.post('/v1/mi-negocio/operativa/hotel/rooms/', data),
  updateHotelRoom: (id: number, data: any) => httpClient.patch(`/v1/mi-negocio/operativa/hotel/rooms/${id}/`, data),
  deleteHotelRoom: (id: number) => httpClient.delete(`/v1/mi-negocio/operativa/hotel/rooms/${id}/`),

  getRestaurantTables: () => httpClient.get('/v1/mi-negocio/operativa/restaurante/tables/'),
  createRestaurantTable: (data: any) => httpClient.post('/v1/mi-negocio/operativa/restaurante/tables/', data),
  updateRestaurantTable: (id: number, data: any) => httpClient.patch(`/v1/mi-negocio/operativa/restaurante/tables/${id}/`, data),
  deleteRestaurantTable: (id: number) => httpClient.delete(`/v1/mi-negocio/operativa/restaurante/tables/${id}/`),

  getKitchenStations: () => httpClient.get('/v1/mi-negocio/operativa/restaurante/stations/'),
  createKitchenStation: (data: any) => httpClient.post('/v1/mi-negocio/operativa/restaurante/stations/', data),
  deleteKitchenStation: (id: number) => httpClient.delete(`/v1/mi-negocio/operativa/restaurante/stations/${id}/`),

  getVehicles: () => httpClient.get('/v1/mi-negocio/operativa/transporte/vehicles/'),
  createVehicle: (data: any) => httpClient.post('/v1/mi-negocio/operativa/transporte/vehicles/', data),
  deleteVehicle: (id: number) => httpClient.delete(`/v1/mi-negocio/operativa/transporte/vehicles/${id}/`),

  getTours: () => httpClient.get('/v1/mi-negocio/operativa/guias/tours/'),

  // Agencias
  getTravelPackages: () => httpClient.get('/v1/mi-negocio/operativa/agencias/packages/'),
  createTravelPackage: (data: any) => httpClient.post('/v1/mi-negocio/operativa/agencias/packages/', data),
  deleteTravelPackage: (id: number) => httpClient.delete(`/v1/mi-negocio/operativa/agencias/packages/${id}/`),

  getProcesosOperativos: () => httpClient.get('/v1/mi-negocio/operativa/procesos/'),
  updateProcesoEstado: (id: string, nuevo_estado: string) => httpClient.post(`/v1/mi-negocio/operativa/procesos/${id}/avanzar_estado/`, { nuevo_estado }),

  // Motor Operativo Genérico (Fase 3)
  getOrdenesOperativas: () => httpClient.get('/v1/mi-negocio/operativa/ordenes/'),
  updateOrdenEstado: (id: string, nuevo_estado: string, motivo: string) => httpClient.post(`/v1/mi-negocio/operativa/ordenes/${id}/cambiar-estado/`, { nuevo_estado, motivo }),
  reportIncidente: (data: any) => httpClient.post('/v1/mi-negocio/operativa/incidencias/', data),

  // --- UNIFICACIÓN TURISMO (PHASE 1) ---
  getUnifiedProviders: () => httpClient.get('/v1/providers/tourism-providers/'),
  getUnifiedBusinessProfile: (id: string) => httpClient.get(`/v1/providers/business-profiles/${id}/`),
  getUnifiedServices: () => httpClient.get('/v1/providers/tourism-services/'),
  getUnifiedReservations: () => httpClient.get('/v1/reservations/tourism-reservations/'),
};
