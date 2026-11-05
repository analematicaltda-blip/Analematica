import httpClient from '../index';

export const contableEndpoints = {
  getPlanCuentas: () => httpClient.get('/v1/mi-negocio/contable/contabilidad/planes-de-cuentas/'),
  getAsientosContables: () => httpClient.get('/v1/mi-negocio/contable/contabilidad/asientos/'),
  createAsientoContable: (data: any) => httpClient.post('/v1/mi-negocio/contable/contabilidad/asientos/', data),
  getLibroDiario: (fechaInicio: string, fechaFin: string) =>
    httpClient.get(`/v1/mi-negocio/contable/contabilidad/asientos/libro_diario/?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`),
  getLibroMayor: (cuentaCodigo: string, fechaInicio: string, fechaFin: string) =>
    httpClient.get(`/v1/mi-negocio/contable/contabilidad/asientos/libro_mayor/?cuenta_codigo=${cuentaCodigo}&fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`),
  getBalanceComprobacion: (periodoId: string) =>
    httpClient.get(`/v1/mi-negocio/contable/contabilidad/asientos/balance_comprobacion/?periodo_id=${periodoId}`),
  getEstadoResultados: (fechaInicio: string, fechaFin: string) =>
    httpClient.get(`/v1/mi-negocio/contable/contabilidad/asientos/estado_resultados/?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`),
  getBalanceGeneral: (fechaCorte: string) =>
    httpClient.get(`/v1/mi-negocio/contable/contabilidad/asientos/balance_general/?fecha_corte=${fechaCorte}`),
  getFlujoCaja: (fechaInicio: string, fechaFin: string) =>
    httpClient.get(`/v1/mi-negocio/contable/contabilidad/asientos/flujo_caja/?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`),
  getConciliacionWallet: (providerId: string) =>
    httpClient.get(`/sarita/trigger-mission/`, {
      params: {
        type: 'CONCILIACION_WALLET',
        parameters: { provider_id: providerId }
      }
    }),
};
