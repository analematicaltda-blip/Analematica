import { RoleUIConfig } from './superadmin';
import {
  FiTrendingUp, FiArrowUpRight, FiArrowDownLeft,
  FiDollarSign, FiCreditCard, FiBookOpen, FiActivity, FiShield
} from 'react-icons/fi';

export const FINANCIERO_CONFIG: RoleUIConfig = {
  role: 'FINANCIERO',
  dashboardTitle: 'Inteligencia Financiera Nodal',
  sidebarSections: [
    {
      title: 'Tesorería',
      links: [
        { href: '/dashboard/prestador/mi-negocio/gestion-financiera', label: 'Dashboard Financiero', icon: FiActivity, intent: 'open.financial.dashboard' },
        { href: '/dashboard/prestador/mi-negocio/gestion-financiera/cuentas-bancarias', label: 'Cuentas Bancarias', icon: FiCreditCard, intent: 'open.bank.accounts' },
        { href: '/dashboard/prestador/mi-negocio/gestion-financiera/transacciones-bancarias', label: 'Movimientos de Caja', icon: FiArrowUpRight, intent: 'open.cashflow' },
      ]
    },
    {
      title: 'Contabilidad',
      links: [
        { href: '/dashboard/prestador/mi-negocio/gestion-contable', label: 'Libros Contables', icon: FiBookOpen, intent: 'open.accounting' },
        { href: '/dashboard/prestador/mi-negocio/gestion-contable/plan-de-cuentas', label: 'Plan de Cuentas', icon: FiShield, intent: 'open.chart.of.accounts' },
      ]
    }
  ],
  kpis: ['cash_on_hand', 'monthly_revenue', 'burn_rate', 'roi_nodal']
};
