export const VOICE_INTENTS = {
  // Navigation
  'open.cashflow': {
    action: 'NAVIGATE',
    path: '/dashboard/prestador/mi-negocio/gestion-financiera/transacciones-bancarias',
    label: 'Flujo de Caja'
  },
  'open.comercial': {
    action: 'NAVIGATE',
    path: '/dashboard/admin-plataforma/gestion-comercial',
    label: 'Gestión Comercial'
  },

  // Data Queries
  'show.sales.month': {
    action: 'QUERY_KPI',
    kpiId: 'monthly_revenue',
    label: 'Ventas del Mes'
  },
  'compare.revenue.q1': {
    action: 'COMPARE_PERIODS',
    periods: ['Q1_current', 'Q1_previous'],
    label: 'Comparativa Q1'
  },

  // Sovereign Actions
  'execute.sovereign.intervention': {
    action: 'MODAL_OPEN',
    modalId: 'sovereign_intervention',
    label: 'Intervención Soberana'
  }
};
