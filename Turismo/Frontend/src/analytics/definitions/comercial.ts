import { KPICategory, KPIBase } from '../types';

export const commercialKPIDefs = {
  CONVERSION_RATE: {
    id: 'conversion_rate',
    name: 'Tasa de Conversión',
    category: KPICategory.COMMERCIAL,
    unit: '%',
    formula: 'Ventas / Leads'
  },
  SALES_CYCLE: {
    id: 'sales_cycle',
    name: 'Ciclo de Venta',
    category: KPICategory.COMMERCIAL,
    unit: 'días',
    formula: 'Tiempo promedio Lead -> Cierre'
  },
  AVG_TICKET: {
    id: 'avg_ticket',
    name: 'Ticket Promedio',
    category: KPICategory.COMMERCIAL,
    unit: '$',
    formula: 'Ingresos / Ventas'
  }
};

export const marketingKPIDefs = {
  CAC: {
    id: 'cac',
    name: 'Costo de Adquisición (CAC)',
    category: KPICategory.MARKETING,
    unit: '$',
    formula: '(Gasto Marketing + Gasto Ventas) / Nuevos Clientes'
  },
  ROI: {
    id: 'roi',
    name: 'Retorno de Inversión (ROI)',
    category: KPICategory.MARKETING,
    unit: 'x',
    formula: '(Ingresos - Inversión) / Inversión'
  }
};
