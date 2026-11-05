'use client';
import React, { useEffect, useState } from 'react';
import { useMiNegocioApi } from '../../../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { FiTrendingUp, FiActivity, FiUsers, FiPieChart, FiBarChart2 } from 'react-icons/fi';

export default function IndicadoresLaboralesPage() {
  const { getNominaIndicadores, isLoading } = useMiNegocioApi();
  const [metrics, setMetrics] = useState<any[]>([]);

  useEffect(() => {
    getNominaIndicadores().then(res => res && setMetrics(res));
  }, [getNominaIndicadores]);

  return (
    <div className="space-y-10 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 className="text-3xl font-black uppercase italic text-slate-900 dark:text-white leading-none mb-3 tracking-tighter">Métricas de Talento Humano</h1>
          <p className="text-slate-500 font-medium">Análisis profundo de costos, rotación y productividad laboral.</p>
        </div>
        <Button className="bg-slate-900 text-white font-black px-10 h-14 rounded-2xl shadow-xl transition-all">
          <FiBarChart2 className="mr-2" /> Reporte de Gerencia
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
         {metrics.map((m, i) => (
            <Card key={i} className="p-10 border-none shadow-sm bg-white dark:bg-brand-deep/10 rounded-[2.5rem] relative overflow-hidden group hover:ring-2 hover:ring-brand transition-all">
               <div className="absolute top-0 right-0 p-10 opacity-[0.03] group-hover:scale-110 transition-transform text-brand">
                  <FiTrendingUp size={180} />
               </div>

               <div className="flex justify-between items-start mb-12 relative z-10">
                  <div>
                     <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-400 mb-2 font-mono">KPI LABORAL</p>
                     <h3 className="text-3xl font-black italic text-slate-800 dark:text-white tracking-tight">{m.nombre}</h3>
                  </div>
                  <Badge className="text-[10px] font-black uppercase tracking-widest px-4 py-2 bg-slate-900 dark:bg-white dark:text-black rounded-lg">{m.periodo}</Badge>
               </div>

               <div className="flex items-end gap-12 relative z-10">
                  <div>
                     <p className="text-[10px] font-black text-slate-400 uppercase mb-3 flex items-center gap-2"><FiActivity className="text-brand" size={14} /> VALOR CONSOLIDADO</p>
                     <p className="text-7xl font-black tracking-tighter text-slate-900 dark:text-white">
                        ${Number(m.valor).toLocaleString()}
                     </p>
                  </div>
               </div>

               <div className="mt-6 flex justify-between items-center relative z-10">
                  <p className="text-[10px] font-bold text-slate-400 uppercase italic">Actualizado: {new Date(m.fecha_calculo).toLocaleDateString()}</p>
                  <Button variant="ghost" className="text-brand font-black uppercase text-[10px] tracking-widest p-0 h-auto">Ver Histórico →</Button>
               </div>
            </Card>
         ))}
      </div>

      {metrics.length === 0 && !isLoading && (
         <div className="p-40 text-center border-2 border-dashed border-slate-200 dark:border-white/5 rounded-[4rem] bg-white/30 dark:bg-transparent">
            <FiPieChart size={80} className="mx-auto mb-6 opacity-5" />
            <p className="text-slate-400 text-lg font-black uppercase italic tracking-widest">Motor Analítico Procesando</p>
            <p className="text-slate-400 text-sm mt-2 max-w-sm mx-auto">SADI está recopilando datos de liquidaciones y novedades para generar los indicadores del periodo.</p>
            <Button className="mt-10 bg-brand text-white font-black px-8 py-3 rounded-xl uppercase text-[10px] tracking-widest">Recalcular KPI</Button>
         </div>
      )}
    </div>
  );
}
