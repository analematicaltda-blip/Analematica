import api from './api';

/**
 * Hallazgo 14: Hidratación de saldos contables reales.
 */

export const getAccountBalances = async () => {
  const response = await api.get('/governance/accounting/balances/');
  return response.data;
};

export const getBalanceGeneral = async (date?: string) => {
  const params = date ? { date } : {};
  const response = await api.get('/governance/accounting/reports/balance-general/', { params });
  return response.data;
};

export const getProfitLoss = async (start: string, end: string) => {
  const response = await api.get('/governance/accounting/reports/p-and-l/', {
    params: { start, end }
  });
  return response.data;
};

const contabilidadService = {
  getAccountBalances,
  getBalanceGeneral,
  getProfitLoss
};

export default contabilidadService;
