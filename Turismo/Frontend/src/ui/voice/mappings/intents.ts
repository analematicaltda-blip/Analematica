export const voiceIntents = {
  // Navegación
  'open.cashflow': { label: 'Abrir flujo de caja', action: '/dashboard/prestador/mi-negocio/gestion-financiera' },
  'open.marketing': { label: 'Ver marketing', action: '/dashboard/prestador/mi-negocio/gestion-comercial' },
  'open.governance': { label: 'Panel de soberanía', action: '/dashboard/admin-plataforma' },

  // Acciones Analíticas
  'show.sales.month': { label: 'Ventas del mes', intent: 'QUERY_SALES' },
  'compare.revenue.q1': { label: 'Comparar ingresos Q1', intent: 'COMPARE_FINANCIAL' },

  // Gobernanza
  'execute.sovereign': { label: 'Ejecutar intervención soberana', intent: 'SOVEREIGN_INTERVENTION' },
  'approve.proposal': { label: 'Aprobar propuesta estratégica', intent: 'STRATEGY_APPROVE' },
};
