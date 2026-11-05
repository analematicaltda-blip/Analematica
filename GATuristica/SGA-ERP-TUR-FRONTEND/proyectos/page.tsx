'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  FiBriefcase,
  FiPlus,
  FiClock,
  FiCheckCircle,
  FiTrendingUp,
  FiActivity,
  FiMap
} from 'react-icons/fi';
import { Badge } from '@/components/ui/Badge';

import { ViewState } from '@/components/ui/ViewState';

export default function ProyectosPage() {
  const activeProjects: any[] = []; // ELIMINACIÓN DE MOCKS

  return (
    <ViewState
        isEmpty={true}
        emptyMessage="MÓDULO NO DISPONIBLE: El dominio de Gestión de Proyectos está explícitamente comentado en el Kernel de URLs del backend. No hay persistencia activa para este módulo."
    >
    <div className="space-y-10 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Análisis y Gestión de Proyectos</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-2">Seguimiento estratégico de iniciativas y despliegue territorial.</p>
        </div>
        <Button className="bg-brand hover:bg-brand-light text-white font-bold px-8 py-6 rounded-2xl transition-all shadow-lg shadow-brand/20">
           <FiPlus className="mr-2" /> Iniciar Proyecto
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
         {/* Proyectos Activos */}
         <Card className="lg:col-span-2 border-none shadow-sm bg-white dark:bg-brand-deep/20 overflow-hidden">
            <CardHeader className="p-8 border-b border-slate-50 dark:border-white/5">
               <CardTitle className="text-xl font-bold flex items-center gap-3">
                  <FiActivity className="text-brand" /> Ejecución en Tiempo Real
               </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
               <div className="divide-y divide-slate-50 dark:divide-white/5">
                  {activeProjects.map((project, i) => (
                    <div key={i} className="p-8 hover:bg-slate-50 dark:hover:bg-white/5 transition-colors">
                       <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-6">
                          <div>
                             <h4 className="text-lg font-bold text-slate-900 dark:text-white mb-1">{project.name}</h4>
                             <p className="text-xs text-slate-400 font-bold uppercase tracking-widest">Budget: {project.budget}</p>
                          </div>
                          <Badge className={project.status === 'IN_PROGRESS' ? 'bg-emerald-100 text-emerald-700' : 'bg-indigo-100 text-indigo-700'}>
                             {project.status === 'IN_PROGRESS' ? 'EN EJECUCIÓN' : 'PLANIFICACIÓN'}
                          </Badge>
                       </div>

                       <div className="space-y-3">
                          <div className="flex justify-between text-xs font-bold mb-1">
                             <span className="text-slate-500 uppercase tracking-tighter">Progreso de la Misión</span>
                             <span className="text-brand">{project.progress}%</span>
                          </div>
                          <div className="h-2 bg-slate-100 dark:bg-white/10 rounded-full overflow-hidden">
                             <div
                               className="h-full bg-brand transition-all duration-1000"
                               style={{ width: `${project.progress}%` }}
                             />
                          </div>
                       </div>

                       <div className="mt-6 flex items-center gap-6 text-xs text-slate-400 font-medium">
                          <div className="flex items-center gap-1.5">
                             <FiClock /> <span>Entrega: {project.deadLine}</span>
                          </div>
                          <div className="flex items-center gap-1.5">
                             <FiCheckCircle /> <span>4/12 Tareas completadas</span>
                          </div>
                       </div>
                    </div>
                  ))}
               </div>
            </CardContent>
         </Card>

         {/* KPIs de Proyectos */}
         <div className="space-y-6">
            <Card className="border-none shadow-sm bg-brand text-white p-8 overflow-hidden relative group">
               <div className="absolute -right-4 -bottom-4 opacity-20 group-hover:scale-110 transition-transform duration-700">
                  <FiTrendingUp size={120} />
               </div>
               <p className="text-xs font-black uppercase tracking-widest text-white/60 mb-2">ROI Proyectado</p>
               <h3 className="text-4xl font-black italic">2.8x</h3>
               <p className="mt-4 text-xs font-medium text-white/80">Basado en el impacto de los nodos activos.</p>
            </Card>

            <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8">
               <h4 className="text-lg font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
                  <FiMap className="text-brand" /> Distribución Geográfica
               </h4>
               <div className="space-y-6">
                  <div>
                     <div className="flex justify-between text-xs font-bold text-slate-500 uppercase mb-2">
                        <span>Puerto Gaitán</span>
                        <span>75%</span>
                     </div>
                     <div className="h-1.5 bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full bg-indigo-500 w-[75%]" />
                     </div>
                  </div>
                  <div>
                     <div className="flex justify-between text-xs font-bold text-slate-500 uppercase mb-2">
                        <span>Meta Regional</span>
                        <span>25%</span>
                     </div>
                     <div className="h-1.5 bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full bg-slate-400 w-[25%]" />
                     </div>
                  </div>
               </div>
               <Button variant="ghost" className="w-full mt-8 text-brand font-black text-xs uppercase tracking-widest border border-slate-100 dark:border-white/5">
                  Ver Mapa de Nodos
               </Button>
            </Card>
         </div>
      </div>
    </div>
    </ViewState>
  );
}
