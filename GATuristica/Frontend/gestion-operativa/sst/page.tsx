'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  FiShield,
  FiPlus,
  FiAlertTriangle,
  FiActivity,
  FiCheckCircle,
  FiFileText,
  FiTrendingUp,
  FiCalendar,
  FiBookOpen,
  FiBell,
  FiArrowRight,
  FiArrowUpRight
} from 'react-icons/fi';
import { Badge } from '@/components/ui/Badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';

export default function SG_SST_Dashboard() {
  const { getSSTDashboard, isLoading } = useMiNegocioApi();
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    getSSTDashboard().then(res => res && setData(res));
  }, [getSSTDashboard]);

  const menuItems = [
    { title: 'Matriz de Riesgos', icon: FiAlertTriangle, color: 'text-amber-500', bg: 'bg-amber-50', path: 'sst/riesgos', desc: 'Identificación y valoración IPERC' },
    { title: 'Incidentes', icon: FiFileText, color: 'text-red-500', bg: 'bg-red-50', path: 'sst/incidentes', desc: 'Registro y seguimiento de eventos' },
    { title: 'Plan Anual', icon: FiCalendar, color: 'text-indigo-500', bg: 'bg-indigo-50', path: 'sst/plan-anual', desc: 'Cronograma de actividades' },
    { title: 'Capacitaciones', icon: FiBookOpen, color: 'text-emerald-500', bg: 'bg-emerald-50', path: 'sst/capacitaciones', desc: 'Formación y competencias' },
    { title: 'Inspecciones', icon: FiCheckCircle, color: 'text-blue-500', bg: 'bg-blue-50', path: 'sst/inspecciones', desc: 'Verificación de condiciones' },
    { title: 'Indicadores', icon: FiTrendingUp, color: 'text-purple-500', bg: 'bg-purple-50', path: 'sst/indicadores', desc: 'KPIs y métricas de gestión' },
  ];

  return (
    <div className="space-y-12 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-4xl font-black text-slate-900 dark:text-white tracking-tighter uppercase italic leading-none mb-3">Centro de Gobierno SGSST</h1>
          <p className="text-slate-500 dark:text-slate-400 text-lg font-medium">Sistema de Gestión de la Seguridad y Salud en el Trabajo.</p>
        </div>
        <div className="flex gap-4">
           <Link href="/dashboard/prestador/mi-negocio/gestion-operativa/sst/alertas">
              <Button variant="outline" className="border-slate-200 dark:border-white/5 font-black text-xs uppercase tracking-widest px-8 h-14 rounded-2xl relative">
                 <FiBell className="mr-2" size={18} />
                 {data?.alertas_activas?.length > 0 && (
                   <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-600 text-white text-[10px] flex items-center justify-center rounded-full border-2 border-white dark:border-brand-deep shadow-sm">{data.alertas_activas.length}</span>
                 )}
                 Alertas
              </Button>
           </Link>
           <Button className="bg-brand text-white font-black px-10 h-14 rounded-2xl shadow-2xl shadow-brand/30 hover:scale-105 active:scale-95 transition-all">
              <FiPlus className="mr-2" size={20} /> Reportar Novedad
           </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
         <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/10 p-10 rounded-[2.5rem] overflow-hidden relative group">
            <div className="absolute right-0 top-0 p-10 opacity-[0.03] text-brand group-hover:scale-110 transition-transform">
               <FiActivity size={180} />
            </div>
            <p className="text-slate-400 font-black uppercase tracking-[0.2em] text-[10px] mb-4 italic font-mono">Tasa Accidentalidad</p>
            <h3 className="text-6xl font-black text-slate-900 dark:text-white tracking-tighter">
               {data?.indicadores?.find((i: any) => i.tipo === 'Accidentalidad')?.valor || '0.0'}%
            </h3>
            <p className="mt-6 text-[10px] text-emerald-600 font-black uppercase tracking-widest flex items-center gap-2 bg-emerald-50 dark:bg-emerald-950/30 w-fit px-4 py-2 rounded-lg">
               <FiCheckCircle size={14} /> Dentro de la Meta Normativa
            </p>
         </Card>

         <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/10 p-10 rounded-[2.5rem] overflow-hidden relative group">
            <div className="absolute right-0 top-0 p-10 opacity-[0.03] text-indigo-600 group-hover:scale-110 transition-transform">
               <FiShield size={180} />
            </div>
            <p className="text-slate-400 font-black uppercase tracking-[0.2em] text-[10px] mb-4 italic font-mono">Cumplimiento Plan</p>
            <h3 className="text-6xl font-black text-slate-900 dark:text-white tracking-tighter">
               {data?.indicadores?.find((i: any) => i.tipo === 'Cumplimiento')?.valor || '85'}%
            </h3>
            <p className="mt-6 text-[10px] text-brand font-black uppercase tracking-widest bg-brand/10 w-fit px-4 py-2 rounded-lg italic">
               Ejecución Año en Curso
            </p>
         </Card>

         <Card className="border-none shadow-2xl bg-slate-900 text-white p-10 rounded-[2.5rem] relative overflow-hidden group">
            <div className="absolute -right-4 -bottom-4 opacity-10 group-hover:scale-110 transition-all duration-700">
               <FiActivity size={200} />
            </div>
            <p className="text-brand-light font-black uppercase tracking-widest text-[10px] mb-6 italic">SADI Intelligence</p>
            <h3 className="text-2xl font-black leading-tight italic tracking-tight mb-8">SADI detectó desviación en inspecciones de extintores en Centro Norte.</h3>
            <Button className="w-full bg-brand hover:bg-brand-light text-white font-black py-5 rounded-2xl text-xs uppercase tracking-widest shadow-lg shadow-brand/20">Programar Intervención</Button>
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
            <h3 className="text-4xl font-black mb-6 italic tracking-tighter">Auditoría SST 100% Estructurada</h3>
            <p className="text-indigo-100 max-w-3xl text-xl leading-relaxed font-medium">El sistema SARITA garantiza la trazabilidad total de riesgos e incidentes. Genera el Reporte de Estándares Mínimos (Resolución 0312) con un solo clic.</p>
            <div className="flex flex-wrap gap-4 mt-12">
               <Button className="bg-white text-indigo-600 hover:bg-indigo-50 font-black py-6 px-12 rounded-2xl text-sm uppercase tracking-widest shadow-xl">Generar Reporte Maestro</Button>
               <Button variant="ghost" className="text-white hover:bg-white/10 font-black py-6 px-10 rounded-2xl text-xs uppercase tracking-widest border border-white/20">Configuración Legal</Button>
            </div>
         </div>
      </Card>
    </div>
  );
}
