import { KPICategory } from '../types';

export const financialKPIDefs = {
  GROSS_MARGIN: {
    id: 'gross_margin',
    name: 'Margen Bruto',
    category: KPICategory.FINANCIAL,
    unit: '%',
    formula: '(Ingresos - Costos) / Ingresos'
  },
  NET_MARGIN: {
    id: 'net_margin',
    name: 'Margen Neto',
    category: KPICategory.FINANCIAL,
    unit: '%',
    formula: 'Utilidad / Ingresos'
  },
  CURRENT_LIQUIDITY: {
    id: 'current_liquidity',
    name: 'Liquidez Corriente',
    category: KPICategory.FINANCIAL,
    unit: 'ratio',
    formula: 'Activos / Pasivos'
  },
  CASH_FLOW_OPERATING: {
    id: 'cfo',
    name: 'Flujo de Caja Operativo',
    category: KPICategory.FINANCIAL,
    unit: '$',
    formula: 'CFO'
  },
  LTV: {
    id: 'ltv',
    name: 'Lifetime Value (LTV)',
    category: KPICategory.FINANCIAL,
    unit: '$',
    formula: 'Ticket Promedio * Frecuencia * Vida Media'
  }
};
