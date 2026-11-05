import httpClient from '../index';

export const financieroEndpoints = {
  getBankAccounts: () => httpClient.get('/v1/mi-negocio/financiera/cuentas-bancarias/'),
  getCashTransactions: () => httpClient.get('/v1/mi-negocio/financiera/ordenes-pago/'),
  getTesoreria: () => httpClient.get('/v1/mi-negocio/financiera/tesoreria/'),
  getEstadoResultados: () => httpClient.get('/v1/mi-negocio/financiera/estado-resultados/'),
  getBalanceGeneral: () => httpClient.get('/v1/mi-negocio/financiera/balance-general/'),
  getProyecciones: () => httpClient.get('/v1/mi-negocio/financiera/proyecciones/'),
  getRiesgos: () => httpClient.get('/v1/mi-negocio/financiera/riesgos/'),
  getPresupuestos: () => httpClient.get('/v1/mi-negocio/financiera/presupuestos/'),
  getCreditos: () => httpClient.get('/v1/mi-negocio/financiera/creditos/'),
  getIndicadores: () => httpClient.get('/v1/mi-negocio/financiera/indicadores/'),
  getAlertas: () => httpClient.get('/v1/mi-negocio/financiera/alertas/'),
  resolverAlerta: (id: string) => httpClient.post(`/v1/mi-negocio/financiera/alertas/${id}/resolver/`),
};
