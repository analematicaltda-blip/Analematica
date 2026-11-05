'use client';
import React, { useEffect, useState } from 'react';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { FiCalendar, FiCheckCircle, FiCircle, FiArrowRight } from 'react-icons/fi';

export default function PlanAnualPage() {
  const { getSSTPlanAnual, isLoading } = useMiNegocioApi();
  const [plan, setPlan] = useState<any>(null);

  useEffect(() => {
    getSSTPlanAnual().then(res => res && setPlan(res[0]));
  }, [getSSTPlanAnual]);

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 className="text-3xl font-black uppercase italic text-slate-900 dark:text-white">Plan Anual de Trabajo</h1>
          <p className="text-slate-500">Cronograma estratégico de actividades SGSST y metas de cumplimiento.</p>
        </div>
        <Button className="bg-brand hover:bg-brand-deep text-white font-black px-8 h-14 rounded-2xl shadow-xl shadow-brand/20 transition-all">
          Configurar Nuevo Plan {plan?.año}
        </Button>
      </div>

      {!plan ? (
        <Card className="p-20 text-center border-2 border-dashed border-slate-200 dark:border-white/5 rounded-[2rem] bg-white/50 dark:bg-transparent">
           <FiCalendar className="mx-auto mb-4 opacity-20" size={64} />
           <p className="text-slate-400 italic font-medium">No se ha cargado el Plan Anual de Trabajo para el periodo actual.</p>
           <Button variant="outline" className="mt-6 font-bold">Inicializar Plan Maestro</Button>
        </Card>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
             <Card className="p-8 border-none shadow-sm bg-slate-900 text-white rounded-[2rem] relative overflow-hidden">
                <div className="absolute right-0 bottom-0 p-4 opacity-10">
                   <FiCalendar size={100} />
                </div>
                <p className="text-[10px] font-black uppercase tracking-widest text-brand-light mb-2">Estado del Sistema</p>
                <h3 className="text-3xl font-black italic">{plan.estado}</h3>
                <p className="mt-4 text-xs font-medium text-slate-400">Vigencia Año Fiscal {plan.año}</p>
             </Card>

             <Card className="p-8 border-none shadow-sm bg-white dark:bg-brand-deep/20 rounded-[2rem]">
                <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-2 font-mono">Avance de Ejecución</p>
                <div className="flex items-baseline gap-2">
                   <h3 className="text-4xl font-black text-slate-900 dark:text-white">{plan.porcentaje_cumplimiento}%</h3>
                   <span className="text-xs text-emerald-500 font-bold">PROGRESO REAL</span>
                </div>
                <div className="mt-6 h-3 bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden">
                   <div className="h-full bg-brand rounded-full transition-all duration-1000 shadow-[0_0_15px_rgba(var(--brand-rgb),0.5)]" style={{width: `${plan.porcentaje_cumplimiento}%`}} />
                </div>
             </Card>

             <Card className="p-8 border-none shadow-sm bg-white dark:bg-brand-deep/20 rounded-[2rem]">
                <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-2 font-mono">Unidades de Cumplimiento</p>
                <h3 className="text-4xl font-black text-slate-900 dark:text-white">{plan.actividades?.length || 0}</h3>
                <p className="mt-4 text-xs text-indigo-600 font-bold uppercase tracking-widest flex items-center gap-2">
                   Tareas Programadas <FiArrowRight />
                </p>
             </Card>
          </div>

          <Card className="border-none shadow-sm overflow-hidden bg-white dark:bg-brand-deep/10 rounded-[2.5rem]">
             <CardHeader className="p-10 border-b border-slate-50 dark:border-white/5 bg-slate-50/50 dark:bg-black/20">
                <CardTitle className="font-black uppercase flex items-center gap-3 text-xl italic text-brand">
                   <FiCalendar /> Cronograma de Actividades Críticas
                </CardTitle>
             </CardHeader>
             <CardContent className="p-0">
                <div className="divide-y divide-slate-50 dark:divide-white/5">
                   {plan.actividades?.map((act: any, i: number) => (
                      <div key={i} className="p-8 hover:bg-slate-50 dark:hover:bg-white/5 flex flex-col md:flex-row md:items-center justify-between gap-6 transition-all duration-300">
                         <div className="flex items-center gap-8">
                            <div className={`p-4 rounded-[1.25rem] transition-all ${act.completada ? 'bg-emerald-100 text-emerald-600' : 'bg-slate-100 text-slate-400 dark:bg-white/5 shadow-inner'}`}>
                               {act.completada ? <FiCheckCircle size={24} /> : <FiCircle size={24} />}
                            </div>
                            <div>
                               <p className={`font-black text-xl tracking-tight transition-all ${act.completada ? 'text-slate-400 line-through italic' : 'text-slate-800 dark:text-slate-200'}`}>
                                  {act.nombre}
                               </p>
                               <div className="flex items-center gap-3 mt-1">
                                  <Badge variant="outline" className="text-[9px] font-black uppercase tracking-widest px-3">OBJETIVO NORMATIVO</Badge>
                                  <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Límite: {new Date(act.fecha_programada).toLocaleDateString()}</p>
                               </div>
                            </div>
                         </div>
                         <div className="flex items-center gap-4">
                            <div className="text-right hidden md:block">
                               <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Ejecutor Asignado</p>
                               <p className="text-xs font-bold text-slate-600 dark:text-slate-400">Soldado #{act.responsable_id?.substring(0,6)}</p>
                            </div>
                            <Button variant={act.completada ? 'outline' : 'default'} className={`rounded-xl font-black uppercase text-[10px] tracking-widest px-6 h-12 ${act.completada ? 'border-emerald-200 text-emerald-700' : 'bg-brand text-white shadow-lg shadow-brand/20'}`}>
                               {act.completada ? 'Analizar Resultados' : 'Cerrar Actividad'}
                            </Button>
                         </div>
                      </div>
                   ))}
                   {(!plan.actividades || plan.actividades.length === 0) && (
                      <div className="p-20 text-center text-slate-400 italic">No hay actividades definidas en este plan.</div>
                   )}
                </div>
             </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
