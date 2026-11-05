'use client';

import { useAuth } from '@/contexts/AuthContext';
import {
  FiChevronDown, FiChevronRight, FiBox, FiStar, FiAward, FiMap, FiTruck,
  FiBriefcase, FiImage, FiBookOpen, FiGrid, FiShoppingCart, FiUser, FiArchive,
  FiTrendingDown, FiDollarSign, FiHome, FiUsers, FiFileText, FiMapPin, FiSettings,
  FiBarChart2, FiShield, FiFolder, FiCamera, FiEdit, FiCalendar, FiClipboard, FiCheckSquare, FiMonitor, FiDownload,
  FiActivity, FiZap, FiCpu, FiTrendingUp, FiClock, FiGlobe, FiTarget, FiCreditCard
} from 'react-icons/fi';
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

// --- Tipos ---
interface NavLink {
  href: string;
  label: string;
  icon: React.ElementType;
  allowedRoles?: string[];
  prestadorCategoria?: string;
}

interface NavSection {
  title: string;
  links: NavLink[];
  isSubSection?: boolean;
}

// --- Componentes de UI ---
const SidebarSkeleton = () => (
  <div className="p-6 animate-pulse bg-white dark:bg-black h-full">
    <div className="h-10 bg-slate-100 dark:bg-brand-deep rounded-xl w-3/4 mb-10"></div>
    <div className="space-y-6">
      {[...Array(4)].map((_, i) => (
        <div key={i}>
          <div className="h-6 bg-slate-50 dark:bg-brand-deep rounded-lg w-1/2 mb-4"></div>
          <div className="space-y-3 pl-4">
            <div className="h-5 bg-slate-50 dark:bg-brand-deep rounded-lg w-5/6"></div>
            <div className="h-5 bg-slate-50 dark:bg-brand-deep rounded-lg w-4/6"></div>
          </div>
        </div>
      ))}
    </div>
  </div>
);

// --- Enlace del Sidebar ---
const SidebarLink = ({ link, isSubSection }: { link: NavLink, isSubSection?: boolean }) => {
  const pathname = usePathname();
  const isActive = pathname === link.href;
  const Icon = link.icon;
  const paddingClass = isSubSection ? 'pl-14' : 'pl-10';

  return (
    <Link href={link.href} passHref>
      <div
        className={`w-full flex items-center pr-4 py-3 text-sm font-bold rounded-xl transition-all duration-300 text-left cursor-pointer group mb-1 ${paddingClass} ${
          isActive
            ? 'bg-brand/10 text-brand dark:bg-brand/20 dark:text-brand-light shadow-sm'
            : 'text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-brand-deep/50 hover:text-slate-900 dark:hover:text-white'
        }`}
      >
        {Icon && <Icon className={`mr-3 h-5 w-5 flex-shrink-0 transition-transform duration-300 ${isActive ? 'scale-110' : 'group-hover:scale-110'}`} />}
        <span className="truncate tracking-tight">{link.label}</span>
      </div>
    </Link>
  );
};

// --- Estructura de Navegación "Mi Negocio" ---
const miNegocioNav: NavSection[] = [
  {
    title: 'Gestión Operativa',
    isSubSection: true,
    links: [
      { href: '/dashboard/prestador/mi-negocio/gestion-operativa/centro-operativo', label: 'Centro de Operaciones', icon: FiActivity },
      { href: '/dashboard/prestador/mi-negocio/gestion-operativa/genericos/perfil', label: 'Mi Perfil', icon: FiUser },
      { href: '/dashboard/prestador/mi-negocio/gestion-operativa/genericos/productos-servicios', label: 'Productos/Servicios', icon: FiBox },
      { href: '/dashboard/prestador/mi-negocio/gestion-operativa/genericos/clientes', label: 'Clientes', icon: FiUsers },
      { href: '/dashboard/prestador/mi-negocio/gestion-operativa/genericos/reservas', label: 'Reservas', icon: FiCalendar },
      { href: '/dashboard/prestador/mi-negocio/gestion-operativa/genericos/valoraciones', label: 'Valoraciones', icon: FiStar },
      { href: '/dashboard/prestador/mi-negocio/gestion-operativa/genericos/documentos', label: 'Documentos', icon: FiAward },
      { href: '/dashboard/prestador/mi-negocio/gestion-operativa/genericos/galeria', label: 'Galería', icon: FiImage },
      { href: '/dashboard/prestador/mi-negocio/gestion-operativa/genericos/estadisticas', label: 'Estadísticas', icon: FiBarChart2 },
      { href: '/dashboard/prestador/mi-negocio/gestion-operativa/genericos/costos', label: 'Costos', icon: FiTrendingDown },
      { href: '/dashboard/prestador/mi-negocio/gestion-operativa/sst', label: 'Seguridad y Salud (SST)', icon: FiShield },
      { href: '/dashboard/prestador/mi-negocio/gestion-operativa/nomina', label: 'Gestión de Nómina', icon: FiUsers },
      { href: '/dashboard/prestador/mi-negocio/gestion-operativa/delivery', label: 'Logística (Delivery)', icon: FiTruck },
    ],
  },
  {
    title: 'Módulos Pro',
    isSubSection: true,
    links: [
      { href: '/dashboard/prestador/mi-negocio/gestion-operativa/especializados/hoteles', label: 'Habitaciones', icon: FiBriefcase, prestadorCategoria: 'hotel' },
      { href: '/dashboard/prestador/mi-negocio/gestion-operativa/especializados/restaurantes', label: 'Control de Salón', icon: FiGrid, prestadorCategoria: 'restaurante' },
      { href: '/dashboard/prestador/mi-negocio/gestion-operativa/especializados/bares', label: 'Operación Nocturna', icon: FiZap, prestadorCategoria: 'bar' },
      { href: '/dashboard/prestador/mi-negocio/gestion-operativa/especializados/guias', label: 'Mis Rutas', icon: FiMap, prestadorCategoria: 'guía' },
      { href: '/dashboard/prestador/mi-negocio/gestion-operativa/especializados/transporte', label: 'Vehículos', icon: FiTruck, prestadorCategoria: 'transporte' },
      { href: '/dashboard/prestador/mi-negocio/gestion-operativa/especializados/agencias', label: 'Paquetes Turísticos', icon: FiBriefcase, prestadorCategoria: 'agencia' },
    ],
  },
  {
    title: 'Gestión Comercial',
    isSubSection: true,
    links: [
      { href: '/dashboard/prestador/mi-negocio/gestion-comercial', label: 'Facturación de Ventas', icon: FiDollarSign },
    ],
  },
  { title: 'Gestión Archivística', isSubSection: true, links: [{ href: '/dashboard/prestador/mi-negocio/gestion-archivistica', label: 'Archivo Digital', icon: FiArchive }] },
  {
    title: 'Monedero Soberano',
    isSubSection: true,
    links: [
      { href: '/dashboard/prestador/mi-negocio/monedero', label: 'Mi Monedero', icon: FiCreditCard },
      { href: '/dashboard/prestador/mi-negocio/monedero/transferencias', label: 'Transferencias', icon: FiZap },
      { href: '/dashboard/prestador/mi-negocio/monedero/comisiones', label: 'Comisiones', icon: FiAward },
    ]
  },
  { title: 'Análisis Financiero', isSubSection: true, links: [{ href: '/dashboard/prestador/mi-negocio/gestion-financiera', label: 'Tesorería', icon: FiTrendingDown }] },
  { title: 'Gestión Contable', isSubSection: true, links: [{ href: '/dashboard/prestador/mi-negocio/gestion-contable', label: 'Libros Contables', icon: FiBookOpen }] },
];

// --- Sección Colapsable ---
const CollapsibleNavSection = ({
  section,
  userRole,
  prestadorCategoria,
}: {
  section: NavSection;
  userRole: string;
  prestadorCategoria?: string;
}) => {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);

  const filteredLinks = section.links.filter((link) => {
    if (link.allowedRoles && !link.allowedRoles.includes(userRole)) return false;
    if (link.prestadorCategoria) {
      if (userRole !== 'PRESTADOR' || !prestadorCategoria) return false;
      return prestadorCategoria.toLowerCase().includes(link.prestadorCategoria);
    }
    return true;
  });

  const isSectionActive = filteredLinks.some((link) => pathname.startsWith(link.href));
  useEffect(() => {
    if (isSectionActive) setIsOpen(true);
  }, [isSectionActive]);

  if (filteredLinks.length === 0) return null;

  const paddingClass = section.isSubSection ? 'pl-8' : 'px-4';

  return (
    <div className="mb-2">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center justify-between w-full py-2.5 text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 rounded-lg transition-colors focus:outline-none ${paddingClass}`}
      >
        <span>{section.title}</span>
        {isOpen ? <FiChevronDown className="h-3 w-3" /> : <FiChevronRight className="h-3 w-3" />}
      </button>
      {isOpen && (
        <div className="mt-1 space-y-px">
          {filteredLinks.map((link) => (
            <SidebarLink key={link.href} link={link} isSubSection={section.isSubSection} />
          ))}
        </div>
      )}
    </div>
  );
};

import { useTenant } from '@/hooks/useTenant';

// --- Componente Principal del Sidebar ---
export default function Sidebar() {
  const { user, isLoading: isAuthLoading } = useAuth();
  const { isLoading: isTenantLoading, tenant } = useTenant();
  const [isMiNegocioOpen, setIsMiNegocioOpen] = useState(true);

  const isLoading = isAuthLoading || isTenantLoading;

  if (isLoading) return <SidebarSkeleton />;
  if (!user) return <aside className="w-72 flex-shrink-0 bg-white dark:bg-black border-r border-slate-100 dark:border-white/5 h-full" />;

  // Prevención de loops: No renderizar menús operativos si el tenant no está resuelto para roles que lo requieren
  const rolesWithEntity = ['ADMIN', 'ADMIN_ENTIDAD', 'PRESTADOR', 'ARTESANO', 'FUNCIONARIO_DIRECTIVO'];
  if (rolesWithEntity.includes(user.role) && !tenant && window.location.hostname === 'localhost') {
      // En localhost, si no hay tenant, permitimos renderizar pero advertimos
      console.warn("S-UCE: Operando en localhost sin contexto de empresa.");
  }

  const prestadorCategoria = user.perfil_prestador?.categoria?.nombre;

  const adminNavSections: NavSection[] = [
    {
      title: 'ERP Sistémico',
      links: [
        { href: '/dashboard/admin-plataforma/gestion-comercial', label: 'Gestión Comercial', icon: FiDollarSign },
        { href: '/dashboard/admin-plataforma/gestion-operativa', label: 'Gestión Operativa', icon: FiGrid },
        { href: '/dashboard/admin-plataforma/gestion-contable', label: 'Gestión Contable', icon: FiBookOpen },
        { href: '/dashboard/admin-plataforma/gestion-financiera', label: 'Gestión Financiera', icon: FiTrendingDown },
        { href: '/dashboard/admin-plataforma/gestion-archivistica', label: 'Gestión Archivística', icon: FiArchive },
      ],
    },
    {
      title: 'Gobernanza IA',
      links: [
 
        { href: '/dashboard/admin-plataforma/doctrina', label: 'Doctrina del Sistema', icon: FiBookOpen },
        { href: '/dashboard/admin-plataforma/legado', label: 'Custodia de Legado', icon: FiShield },
        { href: '/dashboard/admin-plataforma/grc', label: 'Centro GRC (Compliance)', icon: FiShield },
        { href: '/dashboard/admin-plataforma/defensa', label: 'Defensa Soberana', icon: FiShield },
        { href: '/dashboard/admin-plataforma/defensa-predictiva', label: 'Análisis Predictivo', icon: FiZap },
        { href: '/dashboard/admin-plataforma/inteligencia-defensiva', label: 'Inteligencia Defensiva', icon: FiTarget },
        { href: '/dashboard/admin-plataforma/regulacion', label: 'Configuración Regulatoria', icon: FiShield },
        { href: '/dashboard/admin-plataforma/autonomia', label: 'Control de Autonomía', icon: FiCpu },
        { href: '/dashboard/admin-plataforma/agentes', label: 'Jerarquía de Agentes', icon: FiZap },
        { href: '/dashboard/admin-plataforma/log-ejecutivo', label: 'Bitácora de Soberanía', icon: FiFileText },
        { href: '/dashboard/admin-plataforma/memoria', label: 'Memoria Histórica', icon: FiClock },
 
        { href: '/dashboard/admin-plataforma/inteligencia', label: 'Inteligencia de Decisión', icon: FiActivity },
        { href: '/dashboard/admin-plataforma/optimizacion', label: 'Optimización Ecosistema', icon: FiZap },
        { href: '/dashboard/admin-plataforma/rentabilidad', label: 'Análisis de Rentabilidad', icon: FiTrendingUp },
        { href: '/dashboard/admin-plataforma/planes', label: 'Gestión de Planes', icon: FiShield },
        { href: '/dashboard/admin-plataforma/web-content', label: 'Gobernanza Web', icon: FiMonitor },
      ],
    },
    {
      title: 'Contenido y Territorio',
      links: [
        { href: '/dashboard/admin-plataforma/nodos', label: 'Nodos y Territorios', icon: FiGlobe },
        { href: '/dashboard/publicaciones', label: 'Publicaciones', icon: FiFileText },
        { href: '/dashboard/atractivos', label: 'Atractivos Turísticos', icon: FiMapPin },
        { href: '/dashboard/rutas', label: 'Rutas Estratégicas', icon: FiMap },
      ],
    },
    {
      title: 'Administración Core',
      links: [
        { href: '/dashboard/admin/users', label: 'Control de Usuarios', icon: FiUsers },
        { href: '/dashboard/admin/site-config', label: 'Configuración Global', icon: FiSettings },
        { href: '/dashboard/admin/verificacion', label: 'Centro de Verificación', icon: FiCheckSquare },
        { href: '/dashboard/admin/scoring', label: 'Reglas de Puntuación', icon: FiAward },
      ],
    },
  ];

  return (
    <aside className="w-72 flex-shrink-0 bg-white dark:bg-black border-r border-slate-100 dark:border-white/5 flex flex-col h-full transition-colors">
      <div className="p-8 pb-10">
        <div className="flex items-center gap-3 mb-8">
           <div className="w-10 h-10 bg-brand rounded-xl flex items-center justify-center text-white shadow-xl shadow-brand/20">
              <FiShield size={24} />
           </div>
           <div>
              <h2 className="text-2xl font-black text-slate-900 dark:text-white tracking-tighter">SARITA</h2>
              <p className="text-[9px] font-black text-brand uppercase tracking-[0.3em]">Sovereign ERP</p>
           </div>
        </div>

        <div className="bg-slate-50 dark:bg-brand-deep/30 p-4 rounded-2xl border border-slate-100 dark:border-white/5">
           <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-brand/10 dark:bg-brand/20 flex items-center justify-center text-brand">
                 <FiUser size={16} />
              </div>
              <div className="flex-1 min-w-0">
                 <p className="text-xs font-bold text-slate-900 dark:text-white truncate">{user.username}</p>
                 <p className="text-[10px] text-slate-500 dark:text-slate-400 truncate">{user.email}</p>
              </div>
           </div>
           {tenant && (
             <div className="mt-3 pt-3 border-t border-slate-100 dark:border-white/5">
                <p className="text-[9px] font-black uppercase text-brand tracking-widest mb-1">Empresa Activa</p>
                <div className="flex items-center justify-between">
                   <p className="text-[11px] font-bold text-slate-700 dark:text-slate-300 truncate">{tenant.name}</p>
                   <button className="text-[9px] font-black text-brand-deep bg-brand-light px-2 py-0.5 rounded uppercase hover:opacity-80 transition-opacity">Cambiar</button>
                </div>
             </div>
           )}
        </div>
      </div>

      <nav className="flex-1 px-4 space-y-1 overflow-y-auto custom-scrollbar pb-10">
        <SidebarLink link={{ href: '/dashboard', label: 'Dashboard Central', icon: FiHome }} />

        {(user.role === 'PRESTADOR' || user.role === 'ARTESANO') && (
          <div className="mt-8">
            <div className="px-4 mb-4 flex items-center justify-between group cursor-pointer" onClick={() => setIsMiNegocioOpen(!isMiNegocioOpen)}>
               <span className="text-xs font-black text-slate-900 dark:text-white tracking-widest uppercase">
                 {user.role === 'ARTESANO' ? 'Mi Taller' : 'Mi Negocio'}
               </span>
               {isMiNegocioOpen ? <FiChevronDown size={14} className="text-slate-400" /> : <FiChevronRight size={14} className="text-slate-400" />}
            </div>
            {isMiNegocioOpen && (
              <div className="space-y-px">
                {miNegocioNav.map((section) => (
                  <CollapsibleNavSection
                    key={section.title}
                    section={section}
                    userRole={user.role}
                    prestadorCategoria={prestadorCategoria}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {(user.role === 'ADMIN' || user.role === 'FUNCIONARIO_DIRECTIVO') &&
          adminNavSections.map((section) => (
            <CollapsibleNavSection key={section.title} section={section} userRole={user.role} />
          ))}
      </nav>

      <div className="p-6 border-t border-slate-50 dark:border-white/5">
         <div className="bg-indigo-600 rounded-2xl p-6 text-white relative overflow-hidden group cursor-pointer">
            <div className="absolute -right-4 -bottom-4 opacity-20 group-hover:scale-125 transition-transform duration-700">
               <FiZap size={60} />
            </div>
            <p className="text-[10px] font-black uppercase tracking-widest text-indigo-200 mb-1">Status</p>
            <p className="text-xs font-bold leading-tight">Agentes de Inteligencia activos en red.</p>
         </div>
      </div>
    </aside>
  );
}
