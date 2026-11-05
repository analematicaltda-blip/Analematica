'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import {
  FiMap,
  FiActivity,
  FiZap,
  FiTarget,
  FiShield,
  FiTrendingUp,
  FiGrid
} from 'react-icons/fi';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

export default function AdminProyectosSistemicosPage() {
  const regions = [
    { name: 'Sector Puerto Gaitán Centro', projects: 12, impact: 'HIGH', budget: '$45k' },
    { name: 'Corredor Turístico Rio Meta', projects: 8, impact: 'VERY HIGH', budget: '$120k' },
    { name: 'Vereda Cristalina', projects: 4, impact: 'MEDIUM', budget: '$18k' },
  ];

  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      {/* Hero de Proyectos Estratégicos */}
      <div className="bg-slate-900 rounded-[2.5rem] p-12 text-white shadow-2xl relative overflow-hidden">
         <div className="absolute top-0 right-0 p-16 opacity-5">
            <FiTarget size={350} />
         </div>
         <div className="relative z-10">
            <div className="inline-flex items-center gap-2 bg-brand/20 border border-brand/30 px-4 py-2 rounded-full mb-8">
               <div className="w-2 h-2 bg-brand rounded-full animate-pulse" />
               <span className="text-[10px] font-black uppercase tracking-widest text-brand-light">Misiones de Desarrollo Territorial</span>
            </div>
            <h1 className="text-6xl font-black tracking-tighter mb-6 uppercase leading-tight max-w-3xl">Gobernanza de Proyectos Sistémicos</h1>
            <p className="text-xl text-slate-400 leading-relaxed max-w-2xl font-medium">
               Monitoreo de inversiones, despliegue de infraestructura y misiones de impacto económico coordinadas por los agentes SARITA.
            </p>
         </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
         {/* Listado de Misiones */}
         <Card className="lg:col-span-2 border-none shadow-sm bg-white dark:bg-brand-deep/20 rounded-3xl overflow-hidden">
            <CardHeader className="p-10 border-b border-slate-50 dark:border-white/5 flex flex-row items-center justify-between">
               <CardTitle className="text-2xl font-black flex items-center gap-3 italic">
                  <FiGrid className="text-brand" /> Mapa de Ejecución
               </CardTitle>
               <Button variant="ghost" className="text-brand font-black text-xs uppercase tracking-widest">Ver Todas las Misiones</Button>
            </CardHeader>
            <CardContent className="p-0">
               <div className="divide-y divide-slate-50 dark:divide-white/5">
                  {regions.map((region, i) => (
                    <div key={i} className="p-10 hover:bg-slate-50 dark:hover:bg-white/5 transition-all flex flex-col md:flex-row md:items-center justify-between gap-8 group">
                       <div className="flex items-center gap-8">
                          <div className="w-16 h-16 bg-slate-900 rounded-2xl flex items-center justify-center text-white group-hover:bg-brand transition-colors duration-500 shadow-xl shadow-black/20">
                             <FiMap size={32} />
                          </div>
                          <div>
                             <h4 className="text-xl font-black text-slate-900 dark:text-white mb-2">{region.name}</h4>
                             <div className="flex items-center gap-4">
                                <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">{region.projects} Proyectos Activos</span>
                                <span className="text-xs font-black text-brand italic">Impacto: {region.impact}</span>
                             </div>
                          </div>
                       </div>
                       <div className="text-right">
                          <p className="text-2xl font-black text-slate-900 dark:text-white">{region.budget}</p>
                          <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mt-1 italic">Presupuesto Ejecutado</p>
                       </div>
                    </div>
                  ))}
               </div>
            </CardContent>
         </Card>

         {/* Panel Lateral de Soberanía */}
         <div className="space-y-8">
            <Card className="border-none shadow-xl bg-indigo-600 text-white p-10 rounded-3xl relative overflow-hidden">
               <div className="absolute -right-6 -bottom-6 opacity-20 group-hover:scale-110 transition-transform duration-700">
                  <FiTrendingUp size={150} />
               </div>
               <p className="text-xs font-black uppercase tracking-widest text-indigo-200 mb-2">Tasa de Éxito</p>
               <h3 className="text-5xl font-black italic">94.2%</h3>
               <p className="mt-6 text-sm leading-relaxed text-indigo-100 font-medium">Las misiones autonómas han reducido las fugas de presupuesto en un 18%.</p>
               <Button className="w-full bg-white text-indigo-600 font-black py-4 mt-10 rounded-xl">Audit Report</Button>
            </Card>

            <Card className="border-none shadow-sm bg-slate-50 dark:bg-brand-deep/30 p-10 rounded-3xl border border-slate-100 dark:border-white/5">
               <h3 className="text-xl font-black text-slate-900 dark:text-white mb-8 flex items-center gap-3">
                  <FiZap className="text-brand" /> Inteligencia Activa
               </h3>
               <div className="space-y-8">
                  <div className="flex items-start gap-4">
                     <div className="mt-1 w-2 h-2 bg-brand rounded-full animate-ping" />
                     <div>
                        <p className="text-sm font-bold text-slate-800 dark:text-slate-200 leading-tight">Agente 'Capitán Proyectos' detectó demora en Nodo Cristalina.</p>
                        <p className="text-xs text-slate-400 mt-1 uppercase font-black tracking-widest">Hace 5 min</p>
                     </div>
                  </div>
                  <div className="flex items-start gap-4">
                     <div className="mt-1 w-2 h-2 bg-emerald-500 rounded-full" />
                     <div>
                        <p className="text-sm font-bold text-slate-800 dark:text-slate-200 leading-tight">Inyección de capital para turismo ecológico completada con éxito.</p>
                        <p className="text-xs text-slate-400 mt-1 uppercase font-black tracking-widest">Hace 2 horas</p>
                     </div>
                  </div>
               </div>
               <Button variant="outline" className="w-full mt-10 border-slate-200 dark:border-white/5 font-black text-slate-500">Configurar Alertas IA</Button>
            </Card>
         </div>
      </div>
    </div>
  );
}
