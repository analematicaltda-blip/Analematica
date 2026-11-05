import {
  FiHome, FiDollarSign, FiGrid, FiBookOpen,
  FiTrendingUp, FiArchive, FiShield, FiZap,
  FiActivity, FiMonitor, FiUsers, FiSettings,
  FiCheckSquare, FiAward, FiMapPin, FiMap, FiFileText,
  FiMic
} from 'react-icons/fi';

export interface NavLink {
  href: string;
  label: string;
  icon: any;
  intent?: string;
}

export interface NavSection {
  title: string;
  links: NavLink[];
}

export interface RoleUIConfig {
  role: string;
  dashboardTitle: string;
  sidebarSections: NavSection[];
  kpis: string[]; // Identificadores de KPIs permitidos
}

export const SUPERADMIN_CONFIG: RoleUIConfig = {
  role: 'ADMIN',
  dashboardTitle: 'Centro de Soberanía Sistémica',
  sidebarSections: [
    {
      title: 'ERP Sistémico',
      links: [
        { href: '/dashboard/admin-plataforma/gestion-comercial', label: 'Gestión Comercial', icon: FiDollarSign, intent: 'open.comercial' },
        { href: '/dashboard/admin-plataforma/gestion-operativa', label: 'Gestión Operativa', icon: FiGrid, intent: 'open.operativa' },
        { href: '/dashboard/admin-plataforma/gestion-contable', label: 'Gestión Contable', icon: FiBookOpen, intent: 'open.contable' },
        { href: '/dashboard/admin-plataforma/gestion-financiera', label: 'Gestión Financiera', icon: FiTrendingUp, intent: 'open.financiera' },
        { href: '/dashboard/admin-plataforma/gestion-archivistica', label: 'Gestión Archivística', icon: FiArchive, intent: 'open.archivistica' },
      ]
    },
    {
      title: 'Gobernanza IA',
      links: [
        { href: '/dashboard/admin-plataforma/inteligencia', label: 'Inteligencia de Decisión', icon: FiActivity, intent: 'open.intelligence' },
        { href: '/dashboard/admin-plataforma/optimizacion', label: 'Optimización Ecosistema', icon: FiZap, intent: 'open.optimization' },
        { href: '/dashboard/admin-plataforma/rentabilidad', label: 'Análisis de Rentabilidad', icon: FiTrendingUp, intent: 'open.rentabilidad' },
        { href: '/dashboard/admin-plataforma/planes', label: 'Gestión de Planes', icon: FiShield, intent: 'open.planes' },
        { href: '/dashboard/admin-plataforma/web-content', label: 'Gobernanza Web', icon: FiMonitor, intent: 'open.web_governance' },
        { href: '/dashboard/admin-plataforma/auditoria-voz', label: 'Auditoría de Voz', icon: FiMic, intent: 'open.voice_audit' },
      ]
    }
  ],
  kpis: ['ecosystem_revenue', 'verified_providers', 'systemic_roi', 'ai_trust']
};
