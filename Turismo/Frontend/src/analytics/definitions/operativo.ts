import { KPICategory } from '../types';

export const operationalKPIDefs = {
  RESOURCE_UTILIZATION: {
    id: 'resource_utilization',
    name: 'Utilización de Recursos',
    category: KPICategory.OPERATIONAL,
    unit: '%',
    formula: 'Capacidad Real / Capacidad Teórica'
  },
  SERVICE_COMPLIANCE: {
    id: 'service_compliance',
    name: 'Cumplimiento de Servicio (SLA)',
    category: KPICategory.OPERATIONAL,
    unit: '%',
    formula: 'Servicios Exitosos / Totales'
  },
  SST_INCIDENTS: {
    id: 'sst_incidents',
    name: 'Incidencias SST',
    category: KPICategory.OPERATIONAL,
    unit: 'count',
    formula: 'Riesgos o Accidentes Reportados'
  }
};
