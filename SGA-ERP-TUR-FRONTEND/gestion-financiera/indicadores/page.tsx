'use client';

import React, { useEffect, useState } from 'react';
import { useMiNegocioApi } from '../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FiBarChart2, FiActivity, FiTrendingUp, FiShield, FiTrendingDown } from 'react-icons/fi';

export default function IndicadoresPage() {
  const { getIndicadores, isLoading } = useMiNegocioApi();
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    const load = async () => {
      const res = await getIndicadores();
      if (res) setData(res);
    };
    load();
  }, [getIndicadores]);

  const latest = data.slice(0, 4);

  return (
    <div className="space-y-8 py-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Indicadores de Gestión</h1>
          <p className="text-slate-500">Métricas clave de desempeño financiero (KPIs).</p>
        </div>
        <Button className="bg-slate-900 text-white font-black">Recalcular Ahora</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {latest.map((ind) => (
          <Card key={ind.id} className="border-none shadow-sm bg-white p-8 group hover:bg-brand hover:text-white transition-all duration-300">
            <p className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 group-hover:text-white/60 mb-2">{ind.nombre.replace(/_/g, ' ')}</p>
            <p className="text-4xl font-black tracking-tighter mb-4">{parseFloat(ind.valor).toFixed(2)}</p>
            <div className="flex items-center gap-2 text-xs font-bold">
               <FiActivity />
               <span>Historial Estable</span>
            </div>
          </Card>
        ))}
        {data.length === 0 && (
           <div className="col-span-full py-40 text-center opacity-10">
              <FiBarChart2 size={120} className="mx-auto" />
           </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
         <Card className="border-none shadow-sm bg-white overflow-hidden">
            <CardHeader className="p-8 border-b bg-slate-50/50">
               <CardTitle className="flex items-center gap-2 uppercase tracking-tighter font-black">
                  <FiTrendingUp className="text-brand" /> Análisis de Rentabilidad
               </CardTitle>
            </CardHeader>
            <CardContent className="p-8">
               <div className="space-y-6">
                  <div>
                     <div className="flex justify-between mb-2">
                        <span className="text-sm font-bold text-slate-700">Margen Bruto</span>
                        <span className="text-sm font-black text-brand">45%</span>
                     </div>
                     <div className="h-2 bg-slate-100 rounded-full"><div className="h-full bg-brand w-[45%] rounded-full" /></div>
                  </div>
                  <div>
                     <div className="flex justify-between mb-2">
                        <span className="text-sm font-bold text-slate-700">Margen Operativo (EBITDA)</span>
                        <span className="text-sm font-black text-brand">32%</span>
                     </div>
                     <div className="h-2 bg-slate-100 rounded-full"><div className="h-full bg-brand w-[32%] rounded-full" /></div>
                  </div>
                  <div>
                     <div className="flex justify-between mb-2">
                        <span className="text-sm font-bold text-slate-700">Margen Neto</span>
                        <span className="text-sm font-black text-brand">18%</span>
                     </div>
                     <div className="h-2 bg-slate-100 rounded-full"><div className="h-full bg-brand w-[18%] rounded-full" /></div>
                  </div>
               </div>
            </CardContent>
         </Card>

         <Card className="border-none shadow-sm bg-white overflow-hidden">
            <CardHeader className="p-8 border-b bg-slate-50/50">
               <CardTitle className="flex items-center gap-2 uppercase tracking-tighter font-black">
                  <FiShield className="text-blue-600" /> Solvencia y Liquidez
               </CardTitle>
            </CardHeader>
            <CardContent className="p-8">
               <div className="space-y-6">
                  <div className="flex justify-between items-center p-4 bg-blue-50 rounded-2xl">
                     <div>
                        <p className="text-[10px] font-black text-blue-400 uppercase tracking-widest">Razón Corriente</p>
                        <p className="text-2xl font-black text-blue-900">1.82</p>
                     </div>
                     <span className="text-[10px] font-black bg-blue-600 text-white px-3 py-1 rounded-full uppercase">Saludable</span>
                  </div>
                  <div className="flex justify-between items-center p-4 bg-slate-50 rounded-2xl border border-slate-100">
                     <div>
                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Prueba Ácida</p>
                        <p className="text-2xl font-black text-slate-900">1.15</p>
                     </div>
                     <span className="text-[10px] font-black bg-slate-200 text-slate-500 px-3 py-1 rounded-full uppercase">Normal</span>
                  </div>
               </div>
            </CardContent>
         </Card>
      </div>
    </div>
  );
}
