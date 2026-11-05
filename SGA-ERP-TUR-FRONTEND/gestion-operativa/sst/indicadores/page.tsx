'use client';
import React, { useEffect, useState } from 'react';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { FiTrendingUp, FiActivity, FiTarget, FiDownload, FiBarChart2 } from 'react-icons/fi';

export default function IndicadoresPage() {
  const { getSSTIndicadores, isLoading } = useMiNegocioApi();
  const [metrics, setMetrics] = useState<any[]>([]);

  useEffect(() => {
    getSSTIndicadores().then(res => res && setMetrics(res));
  }, [getSSTIndicadores]);

  return (
    <div className="space-y-10 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 className="text-3xl font-black uppercase italic text-slate-900 dark:text-white leading-none mb-3 tracking-tighter">Tablero de Indicadores SST</h1>
          <p className="text-slate-500 font-medium">Análisis de desempeño preventivo y reactivo del sistema de gestión.</p>
        </div>
        <div className="flex gap-4">
           <Button variant="outline" className="font-black text-[10px] uppercase tracking-widest px-8 border-slate-200">Exportar KPI</Button>
           <Button className="bg-brand hover:bg-brand-deep text-white font-black px-10 h-14 rounded-2xl shadow-xl shadow-brand/20 transition-all">
             <FiDownload className="mr-2" /> Reporte de Gestión
           </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
         {metrics.map((m, i) => (
            <Card key={i} className="p-10 border-none shadow-sm bg-white dark:bg-brand-deep/10 rounded-[2.5rem] relative overflow-hidden group hover:ring-2 hover:ring-brand transition-all">
               <div className="absolute top-0 right-0 p-10 opacity-[0.03] group-hover:scale-110 transition-transform text-brand">
                  <FiBarChart2 size={180} />
               </div>

               <div className="flex justify-between items-start mb-12 relative z-10">
                  <div>
                     <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-400 mb-2 font-mono">{m.tipo}</p>
                     <h3 className="text-3xl font-black italic text-slate-800 dark:text-white tracking-tight">{m.nombre}</h3>
                  </div>
                  <Badge className="text-[10px] font-black uppercase tracking-widest px-4 py-2 bg-slate-900 dark:bg-white dark:text-black rounded-lg">{m.periodo}</Badge>
               </div>

               <div className="flex items-end gap-12 relative z-10">
                  <div>
                     <p className="text-[10px] font-black text-slate-400 uppercase mb-3 flex items-center gap-2"><FiActivity className="text-brand" size={14} /> VALOR ACTUAL</p>
                     <p className={`text-7xl font-black tracking-tighter ${Number(m.valor) > Number(m.meta) && (m.tipo === 'Accidentalidad' || m.tipo === 'Severidad') ? 'text-red-600 drop-shadow-[0_0_15px_rgba(220,38,38,0.3)]' : 'text-slate-900 dark:text-white'}`}>
                        {m.valor}<span className="text-2xl font-bold opacity-30">%</span>
                     </p>
                  </div>
                  <div className="pb-2 border-l border-slate-100 dark:border-white/5 pl-8">
                     <p className="text-[10px] font-black text-slate-400 uppercase mb-2 flex items-center gap-2"><FiTarget className="text-indigo-500" size={14} /> META</p>
                     <p className="text-4xl font-black text-slate-300 dark:text-slate-600 font-mono tracking-tighter">{m.meta}%</p>
                  </div>
               </div>

               <div className="mt-12 h-4 bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden shadow-inner p-1">
                  <div
                    className={`h-full rounded-full transition-all duration-1500 ease-out shadow-sm ${
                      (m.tipo === 'Accidentalidad' || m.tipo === 'Severidad')
                        ? (Number(m.valor) <= Number(m.meta) ? 'bg-emerald-500' : 'bg-red-600')
                        : (Number(m.valor) >= Number(m.meta) ? 'bg-emerald-500' : 'bg-amber-500')
                    }`}
                    style={{width: `${Math.min(100, (Number(m.valor) / (Math.max(Number(m.meta), Number(m.valor)) || 1)) * 100)}%`}}
                  />
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
            <FiTrendingUp size={80} className="mx-auto mb-6 opacity-5" />
            <p className="text-slate-400 text-lg font-black uppercase italic tracking-widest">Motor Analítico en Espera</p>
            <p className="text-slate-400 text-sm mt-2 max-w-sm mx-auto">No se han procesado indicadores en el periodo actual. Los datos se consolidan al cierre de cada mes operativo.</p>
            <Button className="mt-10 bg-slate-900 text-white font-black px-8 py-3 rounded-xl uppercase text-[10px] tracking-widest">Forzar Cálculo de KPI</Button>
         </div>
      )}
    </div>
  );
}
