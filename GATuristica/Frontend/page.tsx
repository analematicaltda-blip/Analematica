'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  FiBriefcase, FiCalendar, FiTruck, FiCreditCard,
  FiTrendingUp, FiArrowRight, FiActivity, FiUsers, FiDollarSign, FiShield, FiAward
} from 'react-icons/fi';
import Link from 'next/link';
import { useMiNegocioApi } from './hooks/useMiNegocioApi';

const sections = [
  {
    title: 'Perfil del Prestador',
    desc: 'Gestiona la información legal y de contacto de tu negocio.',
    icon: FiBriefcase,
    href: '/dashboard/prestador/mi-negocio/perfil',
    color: 'bg-blue-100 text-blue-600',
    key: 'profile'
  },
  {
    title: 'Servicios Turísticos',
    desc: 'Administra tu catálogo de habitaciones, tours, platos y más.',
    icon: FiActivity,
    href: '/dashboard/prestador/mi-negocio/servicios',
    color: 'bg-emerald-100 text-emerald-600',
    key: 'services'
  },
  {
    title: 'Reservas Unificadas',
    desc: 'Control total de tus reservas confirmadas y pendientes.',
    icon: FiCalendar,
    href: '/dashboard/prestador/mi-negocio/reservas',
    color: 'bg-purple-100 text-purple-600',
    key: 'reservations'
  },
  {
    title: 'Logística y Delivery',
    desc: 'Gestiona entregas físicas y recocidas de clientes.',
    icon: FiTruck,
    href: '/dashboard/prestador/mi-negocio/delivery',
    color: 'bg-amber-100 text-amber-600',
    key: 'delivery'
  },
  {
    title: 'Monedero Digital',
    desc: 'Consulta tu saldo y retira tus ganancias de forma segura.',
    icon: FiCreditCard,
    href: '/dashboard/prestador/mi-negocio/monedero',
    color: 'bg-indigo-100 text-indigo-600',
    key: 'wallet'
  },
  {
    title: 'Punto de Venta (Web POS)',
    desc: 'Facturación rápida en mostrador, emisión de tickets y cobro directo.',
    icon: FiDollarSign,
    href: '/dashboard/prestador/mi-negocio/pos',
    color: 'bg-green-100 text-green-600',
    key: 'pos'
  },
  {
    title: 'Gestión Operativa y SG-SST',
    desc: 'Procesos operativos, seguridad y salud en el trabajo y nómina.',
    icon: FiShield,
    href: '/dashboard/prestador/mi-negocio/gestion-operativa',
    color: 'bg-teal-100 text-teal-600',
    key: 'operativa'
  },
  {
    title: 'Caracterización Institucional',
    desc: 'Completa tu perfil técnico para la Secretaría de Turismo.',
    icon: FiFileText,
    href: '/dashboard/prestador/mi-negocio/caracterizacion',
    color: 'bg-orange-100 text-orange-600',
    key: 'characterization'
  }
];

import { FiFileText, FiAlertCircle } from 'react-icons/fi';

export default function MiNegocioDashboard() {
  const { getStatistics } = useMiNegocioApi();
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    // getStatistics().then(setStats);
    // Mock data based on real schema
    setStats({
      total_sales: 1250000,
      active_reservations: 12,
      pending_deliveries: 4,
      wallet_balance: 450000
    });
  }, []);

  return (
    <div className="space-y-10 p-6 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-4xl font-black text-slate-900 tracking-tight">Mi Negocio</h1>
          <p className="text-slate-500 mt-2 text-lg">Panel empresarial unificado del ecosistema SARITA.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
         <StatCard title="Ventas del Mes" value={stats?.total_sales} icon={FiTrendingUp} isCurrency />
         <StatCard title="Reservas Activas" value={stats?.active_reservations} icon={FiCalendar} />
         <StatCard title="Puntaje Institucional" value="85" icon={<FiAward className="text-indigo-600"/>} />
         <StatCard title="Saldo Monedero" value={stats?.wallet_balance} icon={FiCreditCard} isCurrency />
      </div>

      <Card className="bg-amber-50 border-amber-100 border-2 rounded-[2rem] p-8 flex items-center gap-6 animate-pulse">
         <div className="w-16 h-16 bg-amber-100 text-amber-600 rounded-2xl flex items-center justify-center shrink-0">
            <FiAlertCircle size={32} />
         </div>
         <div>
            <h3 className="text-xl font-bold text-amber-900">Periodo de Caracterización Activo</h3>
            <p className="text-amber-700 font-medium">Restan 24 días para completar tu caracterización técnica obligatoria. Evita sanciones y mejora tu visibilidad.</p>
         </div>
         <Link href="/dashboard/prestador/mi-negocio/caracterizacion" className="ml-auto">
            <Button className="bg-amber-600 hover:bg-amber-700 text-white font-black px-8">Completar Ahora</Button>
         </Link>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
         {sections.map((sec, i) => (
           <Card key={i} className="group border-none shadow-sm hover:shadow-lg transition-all">
              <CardContent className="p-8">
                 <div className={`w-14 h-14 ${sec.color} rounded-2xl flex items-center justify-center mb-6`}>
                    <sec.icon size={28} />
                 </div>
                 <h3 className="text-xl font-bold text-slate-900 mb-2">{sec.title}</h3>
                 <p className="text-slate-500 text-sm mb-6">{sec.desc}</p>
                 <Link href={sec.href} className="text-indigo-600 font-bold flex items-center gap-2 group-hover:gap-3 transition-all">
                    Entrar <FiArrowRight />
                 </Link>
              </CardContent>
           </Card>
         ))}
      </div>
    </div>
  );
}

function StatCard({ title, value, icon: Icon, isCurrency = false }: any) {
  return (
    <Card className="border-none shadow-sm bg-white">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-slate-500">{title}</p>
            <h4 className="text-2xl font-bold text-slate-900 mt-1">
              {isCurrency ? `$${(value || 0).toLocaleString()}` : value}
            </h4>
          </div>
          <div className="p-3 bg-slate-100 rounded-xl">
            <Icon className="text-slate-600" size={24} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
