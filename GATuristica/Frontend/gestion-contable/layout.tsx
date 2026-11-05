'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  FiHome,
  FiList,
  FiBookOpen,
  FiFileText,
  FiPieChart,
  FiShield,
  FiActivity
} from 'react-icons/fi';

const menuItems = [
  { label: 'Dashboard', href: '/dashboard/prestador/mi-negocio/gestion-contable', icon: FiHome },
  { label: 'Plan de Cuentas', href: '/dashboard/prestador/mi-negocio/gestion-contable/plan-de-cuentas', icon: FiList },
  { label: 'Libro Diario', href: '/dashboard/prestador/mi-negocio/gestion-contable/asientos', icon: FiBookOpen },
  { label: 'Libro Mayor', href: '/dashboard/prestador/mi-negocio/gestion-contable/informes/libro-mayor', icon: FiActivity },
  { label: 'Balance General', href: '/dashboard/prestador/mi-negocio/gestion-contable/informes/balance-general', icon: FiPieChart },
  { label: 'Estado Resultados', href: '/dashboard/prestador/mi-negocio/gestion-contable/informes/estado-resultados', icon: FiFileText },
  { label: 'Conciliación Wallet', href: '/dashboard/prestador/mi-negocio/gestion-contable/tesoreria/conciliacion-wallet', icon: FiShield },
];

export default function GestionContableLayout({ children }: { children: React.ReactNode }) {
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
      <main>
        {children}
      </main>
    </div>
  );
}
