'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  FiUsers,
  FiPlus,
  FiDollarSign,
  FiActivity,
  FiCheckCircle,
  FiFileText,
  FiTrendingUp,
  FiCalendar,
  FiBriefcase,
  FiAlertCircle,
  FiArrowUpRight
} from 'react-icons/fi';
import { Badge } from '@/components/ui/Badge';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';

export default function NominaDashboard() {
  const { getNominaDashboard, isLoading } = useMiNegocioApi();
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    getNominaDashboard().then(res => res && setData(res));
  }, [getNominaDashboard]);

  const menuItems = [
    { title: 'Gestión de Empleados', icon: FiUsers, color: 'text-indigo-500', bg: 'bg-indigo-50', path: 'nomina/empleados', desc: 'Registro y hojas de vida' },
    { title: 'Liquidación de Periodos', icon: FiDollarSign, color: 'text-emerald-500', bg: 'bg-emerald-50', path: 'nomina/liquidaciones', desc: 'Cálculo de nómina y aportes' },
    { title: 'Prestaciones Sociales', icon: FiBriefcase, color: 'text-amber-500', bg: 'bg-amber-50', path: 'nomina/prestaciones', desc: 'Primas, cesantías y vacaciones' },
    { title: 'Novedades', icon: FiCalendar, color: 'text-red-500', bg: 'bg-red-50', path: 'nomina/novedades', desc: 'Incapacidades y ausentismo' },
    { title: 'Seguridad Social', icon: FiCheckCircle, color: 'text-blue-500', bg: 'bg-blue-50', path: 'nomina/seguridad-social', desc: 'Aportes a salud y pensión' },
    { title: 'Indicadores Laborales', icon: FiTrendingUp, color: 'text-purple-500', bg: 'bg-purple-50', path: 'nomina/indicadores', desc: 'Análisis de costos y rotación' },
  ];

  return (
    <div className="space-y-12 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-4xl font-black text-slate-900 dark:text-white tracking-tighter uppercase italic leading-none mb-3">Gobierno de Capital Humano</h1>
          <p className="text-slate-500 dark:text-slate-400 text-lg font-medium">Gestión de Nómina, Prestaciones y Cumplimiento Laboral.</p>
        </div>
        <div className="flex gap-4">
           <Link href="/dashboard/prestador/mi-negocio/gestion-operativa/nomina/alertas">
              <Button variant="outline" className="border-slate-200 dark:border-white/5 font-black text-xs uppercase tracking-widest px-8 h-14 rounded-2xl relative">
                 <FiAlertCircle className="mr-2" size={18} />
                 Alertas Críticas
              </Button>
           </Link>
           <Button className="bg-brand text-white font-black px-10 h-14 rounded-2xl shadow-2xl shadow-brand/30 hover:scale-105 active:scale-95 transition-all">
              <FiPlus className="mr-2" size={20} /> Nueva Liquidación
           </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
         <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/10 p-10 rounded-[2.5rem] overflow-hidden relative group">
            <div className="absolute right-0 top-0 p-10 opacity-[0.03] text-brand group-hover:scale-110 transition-transform">
               <FiUsers size={180} />
            </div>
            <p className="text-slate-400 font-black uppercase tracking-[0.2em] text-[10px] mb-4 italic font-mono">Fuerza Laboral Activa</p>
            <h3 className="text-6xl font-black text-slate-900 dark:text-white tracking-tighter">
               {data?.total_empleados || 0}
            </h3>
            <p className="mt-6 text-[10px] text-emerald-600 font-black uppercase tracking-widest flex items-center gap-2 bg-emerald-50 dark:bg-emerald-950/30 w-fit px-4 py-2 rounded-lg">
               <FiCheckCircle size={14} /> 100% Contratos Vigentes
            </p>
         </Card>

         <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/10 p-10 rounded-[2.5rem] overflow-hidden relative group">
            <div className="absolute right-0 top-0 p-10 opacity-[0.03] text-indigo-600 group-hover:scale-110 transition-transform">
               <FiDollarSign size={180} />
            </div>
            <p className="text-slate-400 font-black uppercase tracking-[0.2em] text-[10px] mb-4 italic font-mono">Última Dispersión</p>
            <h3 className="text-4xl font-black text-slate-900 dark:text-white tracking-tighter">
               ${Number(data?.ultima_nomina?.total_neto || 0).toLocaleString()}
            </h3>
            <p className="mt-6 text-[10px] text-brand font-black uppercase tracking-widest bg-brand/10 w-fit px-4 py-2 rounded-lg italic">
               Periodo: {data?.ultima_nomina?.periodo_fin || 'N/A'}
            </p>
         </Card>

         <Card className="border-none shadow-2xl bg-slate-900 text-white p-10 rounded-[2.5rem] relative overflow-hidden group">
            <div className="absolute -right-4 -bottom-4 opacity-10 group-hover:scale-110 transition-all duration-700">
               <FiActivity size={200} />
            </div>
            <p className="text-brand-light font-black uppercase tracking-widest text-[10px] mb-6 italic">SADI Workforce Insight</p>
            <h3 className="text-2xl font-black leading-tight italic tracking-tight mb-8">El costo laboral se incrementó 4.2% este mes debido a recargos nocturnos.</h3>
            <Button className="w-full bg-brand hover:bg-brand-light text-white font-black py-5 rounded-2xl text-xs uppercase tracking-widest shadow-lg shadow-brand/20">Analizar Desviación</Button>
         </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
         {menuItems.map((item, i) => (
            <Link key={i} href={`/dashboard/prestador/mi-negocio/gestion-operativa/${item.path}`}>
               <Card className="border-none shadow-sm hover:shadow-xl hover:translate-y-[-8px] transition-all p-8 bg-white dark:bg-brand-deep/20 rounded-[2rem] h-full group relative overflow-hidden">
                  <div className={`p-4 rounded-2xl w-fit ${item.bg} dark:bg-white/5 ${item.color} mb-6 transition-all group-hover:scale-110 group-hover:shadow-lg`}>
                     <item.icon size={28} />
                  </div>
                  <h3 className="text-xl font-black text-slate-800 dark:text-white mb-2 tracking-tight flex items-center justify-between">
                     {item.title}
                     <FiArrowUpRight className="opacity-0 group-hover:opacity-100 transition-all text-brand" />
                  </h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400 font-medium leading-relaxed">{item.desc}</p>
               </Card>
            </Link>
         ))}
      </div>

      <Card className="border-none shadow-2xl bg-indigo-600 text-white p-12 rounded-[3rem] relative overflow-hidden group">
         <div className="absolute -left-20 -bottom-20 opacity-20 group-hover:scale-125 transition-transform duration-1000">
            <FiTrendingUp size={400} />
         </div>
         <div className="relative z-10">
            <h3 className="text-4xl font-black mb-6 italic tracking-tighter">Reporte Integrado Contable-Laboral</h3>
            <p className="text-indigo-100 max-w-3xl text-xl leading-relaxed font-medium">El motor de agentes SARITA sincroniza automáticamente cada liquidación con el Libro Diario y el flujo de caja financiero.</p>
            <div className="flex flex-wrap gap-4 mt-12">
               <Button className="bg-white text-indigo-600 hover:bg-indigo-50 font-black py-6 px-12 rounded-2xl text-sm uppercase tracking-widest shadow-xl">Certificado de Aportes</Button>
               <Button variant="ghost" className="text-white hover:bg-white/10 font-black py-6 px-10 rounded-2xl text-xs uppercase tracking-widest border border-white/20">Configuración PILA</Button>
            </div>
         </div>
      </Card>
    </div>
  );
}
