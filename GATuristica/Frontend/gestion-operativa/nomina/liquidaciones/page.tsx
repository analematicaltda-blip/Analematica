'use client';
import React, { useEffect, useState } from 'react';
import { useMiNegocioApi } from '../../../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { FiPlus, FiDollarSign, FiFileText, FiRefreshCw, FiCheckCircle, FiCalendar } from 'react-icons/fi';

export default function LiquidacionesPage() {
  const { getPlanillas, liquidarPlanilla, isLoading } = useMiNegocioApi();
  const [planillas, setPlanillas] = useState<any[]>([]);

  useEffect(() => {
    getPlanillas().then(res => res && setPlanillas(res));
  }, [getPlanillas]);

  const handleLiquidar = async (id: string) => {
     const res = await liquidarPlanilla(id);
     if (res) getPlanillas().then(p => p && setPlanillas(p));
  };

  return (
    <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 className="text-3xl font-black uppercase italic text-slate-900 dark:text-white tracking-tighter">Liquidación de Nómina</h1>
          <p className="text-slate-500 font-medium">Procesamiento masivo de compensaciones por periodo fiscal.</p>
        </div>
        <Button className="bg-emerald-600 hover:bg-emerald-700 text-white font-black px-8 h-14 rounded-2xl shadow-xl shadow-emerald-600/20 group transition-all">
          <FiPlus className="mr-2 group-hover:scale-125 transition-transform" /> Iniciar Periodo de Nómina
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {planillas.map((p, i) => (
          <Card key={i} className="border-none shadow-sm overflow-hidden bg-white dark:bg-brand-deep/10 rounded-[2rem]">
            <div className="flex flex-col md:flex-row">
               <div className={`w-2 ${p.estado === 'BORRADOR' ? 'bg-amber-400' : p.estado === 'LIQUIDADA' ? 'bg-blue-500' : 'bg-emerald-500'}`} />
               <div className="p-8 flex-1 flex flex-col md:flex-row items-center justify-between gap-8">
                  <div className="flex items-center gap-6">
                     <div className="p-4 bg-slate-50 dark:bg-black/40 rounded-2xl text-slate-400">
                        <FiCalendar size={24} />
                     </div>
                     <div>
                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Ciclo de Nómina</p>
                        <h3 className="text-xl font-black text-slate-800 dark:text-white tracking-tight italic">
                           {new Date(p.periodo_inicio).toLocaleDateString()} — {new Date(p.periodo_fin).toLocaleDateString()}
                        </h3>
                     </div>
                  </div>

                  <div className="flex flex-wrap justify-center gap-10">
                     <div className="text-center">
                        <p className="text-[10px] font-black text-slate-400 uppercase mb-1">Total Devengado</p>
                        <p className="text-lg font-black text-slate-900 dark:text-white">${Number(p.total_devengado).toLocaleString()}</p>
                     </div>
                     <div className="text-center">
                        <p className="text-[10px] font-black text-slate-400 uppercase mb-1">Total Deducciones</p>
                        <p className="text-lg font-black text-red-600">-${Number(p.total_deduccion).toLocaleString()}</p>
                     </div>
                     <div className="text-center">
                        <p className="text-[10px] font-black text-slate-400 uppercase mb-1">Neto a Dispersar</p>
                        <p className="text-xl font-black text-emerald-600">${Number(p.total_neto).toLocaleString()}</p>
                     </div>
                  </div>

                  <div className="flex items-center gap-4">
                     <Badge className={
                        p.estado === 'BORRADOR' ? 'bg-amber-100 text-amber-700' :
                        p.estado === 'LIQUIDADA' ? 'bg-blue-100 text-blue-700' :
                        'bg-emerald-100 text-emerald-700'
                     }>
                        {p.estado}
                     </Badge>

                     <div className="flex gap-2">
                        {p.estado === 'BORRADOR' && (
                           <Button onClick={() => handleLiquidar(p.id)} disabled={isLoading} className="bg-brand text-white font-black uppercase text-[10px] tracking-widest px-6 h-12 rounded-xl">
                              <FiRefreshCw className={`mr-2 ${isLoading ? 'animate-spin' : ''}`} /> Ejecutar Cálculo
                           </Button>
                        )}
                        {p.estado === 'LIQUIDADA' && (
                           <Button className="bg-slate-900 text-white font-black uppercase text-[10px] tracking-widest px-6 h-12 rounded-xl">
                              <FiCheckCircle className="mr-2" /> Contabilizar
                           </Button>
                        )}
                        <Button variant="ghost" className="text-brand font-black uppercase text-[10px] tracking-widest h-12 rounded-xl px-4">Detalles</Button>
                     </div>
                  </div>
               </div>
            </div>
          </Card>
        ))}

        {planillas.length === 0 && !isLoading && (
          <div className="p-32 text-center border-2 border-dashed border-slate-200 dark:border-white/5 rounded-[3rem] text-slate-400 italic bg-white/30">
            <FiDollarSign className="mx-auto mb-4 opacity-5" size={64} />
            No se encuentran ciclos de nómina registrados.
          </div>
        )}
      </div>
    </div>
  );
}
