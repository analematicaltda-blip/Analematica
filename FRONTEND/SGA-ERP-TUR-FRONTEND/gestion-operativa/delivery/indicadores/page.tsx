'use client';

import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, DollarSign, Clock, CheckCircle2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';

export default function DeliveryIndicadoresPage() {
  const { fetchData, postData } = useMiNegocioApi('delivery/indicadores');
  const [indicadores, setIndicadores] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadIndicadores();
  }, []);

  const loadIndicadores = async () => {
    try {
      const data = await fetchData();
      setIndicadores(data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    await postData('refresh/', { provider_id: 'c6e7f38a-6aa2-48a9-8279-97168623cb7f' });
    loadIndicadores();
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold flex items-center gap-2 text-gray-800">
          <BarChart3 className="h-6 w-6 text-indigo-600" />
          Indicadores de Desempeño Logístico
        </h1>
        <button
          onClick={handleRefresh}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-indigo-700 shadow-md transition-all"
        >
          Recalcular KPIs
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {indicadores.map((ind) => (
          <Card key={ind.id} className="border-none shadow-lg hover:scale-[1.02] transition-transform cursor-pointer overflow-hidden">
             <div className="h-2 bg-indigo-500 w-full"></div>
             <CardHeader className="pb-2">
                <CardTitle className="text-xs font-bold text-gray-400 uppercase tracking-widest">{ind.nombre}</CardTitle>
             </CardHeader>
             <CardContent className="space-y-4">
                <div className="flex items-baseline gap-2">
                   <div className="text-4xl font-black text-gray-900">
                     {ind.nombre.includes('Costo') ? `$${Number(ind.valor).toLocaleString()}` : Number(ind.valor).toLocaleString()}
                   </div>
                   <div className="text-xs font-bold text-green-500 flex items-center gap-0.5">
                     <TrendingUp className="h-3 w-3" /> +4.2%
                   </div>
                </div>
                <div className="text-xs text-gray-500">Periodo: {ind.periodo}</div>
                <div className="h-1.5 w-full bg-gray-100 rounded-full">
                   <div className="h-1.5 bg-indigo-600 rounded-full" style={{ width: '75%' }}></div>
                </div>
             </CardContent>
          </Card>
        ))}
      </div>

      {/* Gráficos simulados */}
      <Card className="border-none shadow-xl bg-gray-900 text-white">
        <CardHeader>
          <CardTitle>Eficiencia de Entregas Semanal</CardTitle>
        </CardHeader>
        <CardContent>
           <div className="h-48 flex items-end justify-between gap-2 px-4">
              {[45, 80, 60, 95, 70, 85, 90].map((val, i) => (
                <div key={i} className="flex flex-col items-center gap-2 flex-1 group">
                   <div
                      className="w-full bg-indigo-500 rounded-t-lg transition-all group-hover:bg-indigo-400 relative"
                      style={{ height: `${val}%` }}
                   >
                     <span className="absolute -top-6 left-1/2 -translate-x-1/2 text-[10px] font-bold opacity-0 group-hover:opacity-100">{val}%</span>
                   </div>
                   <span className="text-[10px] text-gray-500">Día {i+1}</span>
                </div>
              ))}
           </div>
        </CardContent>
      </Card>
    </div>
  );
}
