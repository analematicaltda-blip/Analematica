'use client';

import React, { useEffect, useState } from 'react';
import { useMiNegocioApi } from '../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FiTrendingUp, FiCloudRain, FiSun, FiActivity } from 'react-icons/fi';

export default function ProyeccionesPage() {
  const { getProyecciones, isLoading } = useMiNegocioApi();
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    const load = async () => {
      const res = await getProyecciones();
      if (res) setData(res);
    };
    load();
  }, [getProyecciones]);

  return (
    <div className="space-y-8 py-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Proyecciones de Flujo</h1>
          <p className="text-slate-500">Escenarios predictivos basados en comportamiento histórico e IA.</p>
        </div>
        <div className="flex gap-2">
           <Button variant="outline" className="font-bold border-slate-200">Optimista</Button>
           <Button variant="outline" className="font-bold border-slate-200">Conservador</Button>
           <Button className="bg-slate-900 text-white font-black px-6">Ejecutar Simulación IA</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data.map((p: any) => (
          <Card key={p.id} className="border-none shadow-sm bg-white overflow-hidden group hover:shadow-xl transition-all">
            <div className="bg-slate-50 p-6 flex justify-between items-center">
               <div>
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-1">Periodo</p>
                  <p className="font-black text-slate-800">{new Date(p.fecha_inicio).toLocaleDateString(undefined, {month: 'long', year: 'numeric'})}</p>
               </div>
               <div className={`w-10 h-10 rounded-full flex items-center justify-center ${p.nivel_probabilidad > 0.7 ? 'bg-green-100 text-green-600' : 'bg-amber-100 text-amber-600'}`}>
                  {p.nivel_probabilidad > 0.7 ? <FiSun /> : <FiCloudRain />}
               </div>
            </div>
            <CardContent className="p-8 space-y-6">
               <div className="flex justify-between items-end border-b border-slate-50 pb-4">
                  <span className="text-xs font-bold text-slate-500 uppercase">Ingresos Estimados</span>
                  <span className="text-xl font-black text-brand">${parseFloat(p.ingresos_proyectados).toLocaleString()}</span>
               </div>
               <div className="flex justify-between items-end border-b border-slate-50 pb-4">
                  <span className="text-xs font-bold text-slate-500 uppercase">Gastos Estimados</span>
                  <span className="text-xl font-black text-red-500">${parseFloat(p.gastos_proyectados).toLocaleString()}</span>
               </div>
               <div className="flex justify-between items-end pt-2">
                  <span className="text-xs font-black text-slate-400 uppercase tracking-widest">Resultado Neto</span>
                  <span className="text-2xl font-black text-slate-900">${(parseFloat(p.ingresos_proyectados) - parseFloat(p.gastos_proyectados)).toLocaleString()}</span>
               </div>
            </CardContent>
          </Card>
        ))}

        {data.length === 0 && (
           <div className="col-span-full py-40 text-center flex flex-col items-center opacity-20">
              <FiTrendingUp size={80} className="text-slate-400 mb-4" />
              <p className="text-2xl font-black uppercase tracking-tighter">Sin proyecciones generadas</p>
           </div>
        )}
      </div>

      <Card className="bg-brand-deep text-white p-12 rounded-3xl overflow-hidden relative shadow-2xl">
         <div className="max-w-2xl relative z-10">
            <h3 className="text-3xl font-black tracking-tight mb-4 text-brand-light">SARITA Forecast Engine</h3>
            <p className="text-brand-light/60 text-lg leading-relaxed">
               Nuestra IA analiza más de 20 variables, incluyendo festividades en Puerto Gaitán, clima y tendencias de reserva para darte una precisión del 94% en tu flujo de caja.
            </p>
         </div>
         <FiActivity size={300} className="absolute right-[-50px] bottom-[-100px] text-white opacity-5" />
      </Card>
    </div>
  );
}
