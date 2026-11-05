'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  FiUsers,
  FiBox,
  FiCalendar,
  FiClock,
  FiTrendingUp,
  FiArrowRight,
  FiZap,
  FiActivity
} from 'react-icons/fi';
import Link from 'next/link';

const modules = [
  {
    title: 'Centro de Operaciones',
    desc: 'Motor de ejecución. Descompón servicios en tareas, asigna responsables y mide tiempos.',
    icon: FiActivity,
    href: '/dashboard/prestador/mi-negocio/gestion-operativa/centro-operativo',
    color: 'bg-emerald-100 text-emerald-600',
    stats: '2 Activas'
  },
  {
    title: 'CRM y Clientes',
    desc: 'Gestión de base de datos de turistas, historial y preferencias.',
    icon: FiUsers,
    href: '/dashboard/prestador/mi-negocio/gestion-operativa/genericos/clientes',
    color: 'bg-blue-100 text-blue-600',
    stats: '124 Turistas'
  },
  {
    title: 'Productos y Servicios',
    desc: 'Catálogo de oferta, precios, inventario y disponibilidad.',
    icon: FiBox,
    href: '/dashboard/prestador/mi-negocio/gestion-operativa/genericos/productos-servicios',
    color: 'bg-indigo-100 text-indigo-600',
    stats: '12 Activos'
  },
  {
    title: 'Reservas y Agenda',
    desc: 'Control de calendario, check-ins y disponibilidad en tiempo real.',
    icon: FiCalendar,
    href: '/dashboard/prestador/mi-negocio/gestion-operativa/genericos/reservas',
    color: 'bg-purple-100 text-purple-600',
    stats: '8 Pendientes'
  },
  {
    title: 'Valoraciones',
    desc: 'Análisis de reputación online y feedback de clientes.',
    icon: FiZap,
    href: '/dashboard/prestador/mi-negocio/gestion-operativa/genericos/valoraciones',
    color: 'bg-yellow-100 text-yellow-600',
    stats: '4.8 Estrellas'
  }
];

import { useMiNegocioApi } from '../hooks/useMiNegocioApi';

export default function GestionOperativaPage() {
  const { getStatistics, isLoading } = useMiNegocioApi();
  const [statsData, setStatsData] = React.useState<any>(null);

  React.useEffect(() => {
    getStatistics().then(res => res && setStatsData(res));
  }, [getStatistics]);

  const dynamicModules = modules.map(mod => {
    let stat = mod.stats;
    if (mod.title === 'Centro de Operaciones' && statsData?.tareas_activas) stat = `${statsData.tareas_activas} Activas`;
    if (mod.title === 'CRM y Clientes' && statsData?.total_clientes) stat = `${statsData.total_clientes} Turistas`;
    if (mod.title === 'Productos y Servicios' && statsData?.total_productos) stat = `${statsData.total_productos} Activos`;
    if (mod.title === 'Reservas y Agenda' && statsData?.reservas_pendientes) stat = `${statsData.reservas_pendientes} Pendientes`;
    if (mod.title === 'Valoraciones' && statsData?.rating_promedio) stat = `${statsData.rating_promedio} Estrellas`;
    return { ...mod, stats: stat };
  });

  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-4xl font-black text-slate-900 tracking-tight">Gestión Operativa</h1>
          <p className="text-slate-500 mt-2 text-lg">El motor de tu negocio turístico. Organiza, escala y automatiza.</p>
        </div>
        <div className="flex bg-slate-100 p-1 rounded-xl">
           <button className="px-6 py-2 bg-white shadow-sm rounded-lg text-sm font-bold text-slate-900">Vista General</button>
           <button className="px-6 py-2 text-sm font-bold text-slate-500 hover:text-slate-700">Módulos Pro</button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
         {dynamicModules.map((mod, i) => (
           <Card key={i} className="group border-none shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 bg-white">
              <CardContent className="p-8">
                 <div className={`w-14 h-14 ${mod.color} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                    <mod.icon size={28} />
                 </div>
                 <h3 className="text-xl font-bold text-slate-900 mb-2">{mod.title}</h3>
                 <p className="text-slate-500 text-sm leading-relaxed mb-6 h-12 overflow-hidden">{mod.desc}</p>
                 <div className="flex items-center justify-between border-t pt-6">
                    <span className="text-xs font-black uppercase tracking-widest text-slate-400">{mod.stats}</span>
                    <Link href={mod.href}>
                       <div className="text-indigo-600 p-2 hover:bg-indigo-50 rounded-full transition-colors">
                          <FiArrowRight size={20} />
                       </div>
                    </Link>
                 </div>
              </CardContent>
           </Card>
         ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
         <Card className="lg:col-span-2 border-none shadow-sm bg-slate-900 text-white overflow-hidden relative">
            <div className="absolute -right-20 -bottom-20 opacity-10">
               <FiTrendingUp size={300} />
            </div>
            <CardContent className="p-10 relative z-10">
               <h2 className="text-2xl font-bold mb-4">Optimización de Capacidad</h2>
               <p className="text-slate-400 mb-8 max-w-md text-lg">He analizado tus reservas de los últimos 3 meses. Podrías aumentar tu rentabilidad en un 15% ajustando los precios para los fines de semana de Agosto.</p>
               <Button className="bg-indigo-500 hover:bg-indigo-400 text-white font-bold py-6 px-8 rounded-xl shadow-lg shadow-indigo-500/30">
                  Ver Recomendación IA
               </Button>
            </CardContent>
         </Card>

         <Card className="border-none shadow-sm bg-white">
            <CardHeader>
               <CardTitle className="flex items-center gap-2 text-lg">
                  <FiClock className="text-indigo-600" /> Próximos Check-ins
               </CardTitle>
            </CardHeader>
            <CardContent>
               <div className="space-y-6">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="flex items-center gap-4 group cursor-pointer">
                       <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 group-hover:bg-indigo-100 group-hover:text-indigo-600 transition-colors">
                          <FiUsers size={20} />
                       </div>
                       <div className="flex-1">
                          <p className="font-bold text-slate-900">Familia Rodriguez</p>
                          <p className="text-xs text-slate-500">2 Adultos • 1 Niño</p>
                       </div>
                       <div className="text-right">
                          <p className="text-xs font-black text-indigo-600 uppercase">Hoy</p>
                          <p className="text-[10px] text-slate-400 font-bold">14:00</p>
                       </div>
                    </div>
                  ))}
                  <Button variant="ghost" className="w-full text-indigo-600 hover:bg-indigo-50 font-bold">Ver todos los eventos</Button>
               </div>
            </CardContent>
         </Card>
      </div>
    </div>
  );
}
