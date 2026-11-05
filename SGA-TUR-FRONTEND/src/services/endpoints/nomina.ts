import httpClient from '../index';

export const nominaEndpoints = {
  getDashboard: () => httpClient.get('/nomina/dashboard/'),
  getEmpleados: () => httpClient.get('/nomina/empleados/'),
  createEmpleado: (data: any) => httpClient.post('/nomina/empleados/', data),
  updateEmpleado: (id: string, data: any) => httpClient.patch(`/nomina/empleados/${id}/`, data),
  deleteEmpleado: (id: string) => httpClient.delete(`/nomina/empleados/${id}/`),

  getPlanillas: () => httpClient.get('/nomina/planillas/'),
  getPlanillaDetalle: (id: string) => httpClient.get(`/nomina/planillas/${id}/`),
  createPlanilla: (data: any) => httpClient.post('/nomina/planillas/', data),
  liquidarPlanilla: (id: string) => httpClient.post(`/nomina/planillas/${id}/liquidar/`),
  contabilizarPlanilla: (id: string) => httpClient.post(`/nomina/planillas/${id}/contabilizar/`),

  getNovedades: () => httpClient.get('/nomina/novedades/'),
  createNovedad: (data: any) => httpClient.post('/nomina/novedades/', data),

  getIncapacidades: () => httpClient.get('/nomina/incapacidades/'),
  getAusencias: () => httpClient.get('/nomina/ausencias/'),
  getIndicadores: () => httpClient.get('/nomina/indicadores/'),

  getConceptos: () => httpClient.get('/nomina/conceptos/'),
};
