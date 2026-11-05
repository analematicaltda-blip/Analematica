'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  FiHome,
  FiCreditCard,
  FiList,
  FiZap,
  FiAward,
  FiShield,
  FiAlertCircle,
  FiSearch,
  FiSettings,
  FiUserCheck
} from 'react-icons/fi';

const menuItems = [
  { label: 'Dashboard', href: '/dashboard/prestador/mi-negocio/monedero', icon: FiHome },
  { label: 'Cuentas', href: '/dashboard/prestador/mi-negocio/monedero/cuentas', icon: FiCreditCard },
  { label: 'Transacciones', href: '/dashboard/prestador/mi-negocio/monedero/transacciones', icon: FiList },
  { label: 'Transferencias', href: '/dashboard/prestador/mi-negocio/monedero/transferencias', icon: FiZap },
  { label: 'Comisiones', href: '/dashboard/prestador/mi-negocio/monedero/comisiones', icon: FiAward },
  { label: 'Retenciones', href: '/dashboard/prestador/mi-negocio/monedero/retenciones', icon: FiShield },
  { label: 'Alertas', href: '/dashboard/prestador/mi-negocio/monedero/alertas', icon: FiAlertCircle },
  { label: 'Auditoría', href: '/dashboard/prestador/mi-negocio/monedero/auditoria', icon: FiSearch },
  { label: 'Reglas', href: '/dashboard/prestador/mi-negocio/monedero/reglas', icon: FiSettings },
  { label: 'Antifraude', href: '/dashboard/prestador/mi-negocio/monedero/antifraude', icon: FiUserCheck },
];

export default function MonederoLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex flex-col space-y-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-black tracking-tighter text-slate-900 dark:text-white uppercase">
          Monedero Soberano <span className="text-brand">SARITA</span>
        </h1>
        <p className="text-slate-500 dark:text-slate-400 text-sm font-medium">
          Infraestructura financiera digital de alta seguridad e integridad forense.
        </p>
      </div>

      <nav className="flex items-center gap-1 overflow-x-auto pb-2 scrollbar-hide border-b border-slate-100 dark:border-white/5">
        {menuItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-2 px-4 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all whitespace-nowrap
                ${isActive
                  ? 'bg-brand text-white shadow-lg shadow-brand/20'
                  : 'text-slate-500 hover:bg-slate-50 dark:hover:bg-white/5'
                }`}
            >
              <item.icon size={14} />
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
