'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  FiHome,
  FiDollarSign,
  FiTarget,
  FiTrendingUp,
  FiCreditCard,
  FiBarChart2,
  FiFileText
} from 'react-icons/fi';

const menuItems = [
  { label: 'Dashboard', href: '/dashboard/prestador/mi-negocio/gestion-financiera', icon: FiHome },
  { label: 'Tesorería', href: '/dashboard/prestador/mi-negocio/gestion-financiera/tesoreria', icon: FiDollarSign },
  { label: 'Conciliación', href: '/dashboard/prestador/mi-negocio/gestion-financiera/conciliacion', icon: FiShield },
  { label: 'Presupuestos', href: '/dashboard/prestador/mi-negocio/gestion-financiera/presupuestos', icon: FiTarget },
  { label: 'Proyecciones', href: '/dashboard/prestador/mi-negocio/gestion-financiera/proyecciones', icon: FiTrendingUp },
  { label: 'Créditos', href: '/dashboard/prestador/mi-negocio/gestion-financiera/creditos', icon: FiCreditCard },
  { label: 'Indicadores', href: '/dashboard/prestador/mi-negocio/gestion-financiera/indicadores', icon: FiBarChart2 },
  { label: 'Reportes', href: '/dashboard/prestador/mi-negocio/gestion-financiera/reportes', icon: FiFileText },
  { label: 'Alertas', href: '/dashboard/prestador/mi-negocio/gestion-financiera/alertas', icon: FiAlertCircle },
  { label: 'Configuración', href: '/dashboard/prestador/mi-negocio/gestion-financiera/configuracion', icon: FiSettings },
];

export default function GestionFinancieraLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex flex-col space-y-6">
      <nav className="flex items-center gap-1 overflow-x-auto pb-2 scrollbar-hide border-b border-slate-100 dark:border-white/5">
        {menuItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-2 px-4 py-3 rounded-xl text-xs font-bold uppercase tracking-widest transition-all whitespace-nowrap
                ${isActive
                  ? 'bg-brand text-white shadow-lg shadow-brand/20'
                  : 'text-slate-500 hover:bg-slate-50 dark:hover:bg-white/5'
                }`}
            >
              <item.icon size={16} />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <main className="animate-in fade-in slide-in-from-bottom-4 duration-700">
        {children}
      </main>
    </div>
  );
}
