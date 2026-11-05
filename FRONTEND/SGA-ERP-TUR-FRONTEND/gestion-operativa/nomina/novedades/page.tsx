'use client';
import React, { useEffect, useState } from 'react';
import { useMiNegocioApi } from '../../../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { FiPlus, FiAlertTriangle, FiClock, FiCalendar, FiArrowRight, FiCheckCircle } from 'react-icons/fi';

export default function NovedadesPage() {
  const { getNominaNovedades, isLoading } = useMiNegocioApi();
  const [novelties, setNovelties] = useState<any[]>([]);

  useEffect(() => {
    getNominaNovedades().then(res => res && setNovelties(res));
  }, [getNominaNovedades]);

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 className="text-3xl font-black uppercase italic text-slate-900 dark:text-white tracking-tighter">Novedades y Ausentismo</h1>
          <p className="text-slate-500 font-medium">Control de incapacidades, licencias, permisos y extras.</p>
        </div>
        <Button className="bg-red-600 hover:bg-red-700 text-white font-black px-8 h-14 rounded-2xl shadow-xl shadow-red-600/20 transition-all">
          <FiPlus className="mr-2" /> Reportar Novedad
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
         <Card className="p-8 border-none shadow-sm bg-white dark:bg-brand-deep/20 rounded-[2.5rem]">
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Incapacidades Activas</p>
            <h3 className="text-4xl font-black text-red-600">3</h3>
            <p className="mt-4 text-xs font-bold text-slate-400 flex items-center gap-2">
               <FiClock /> Pendientes de validar en PILA
            </p>
         </Card>
         <Card className="p-8 border-none shadow-sm bg-white dark:bg-brand-deep/20 rounded-[2.5rem]">
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Permisos Solicitados</p>
            <h3 className="text-4xl font-black text-indigo-600">12</h3>
            <p className="mt-4 text-xs font-bold text-emerald-500 flex items-center gap-2">
               <FiCheckCircle size={12} /> 10 Aprobados por Sargentos
            </p>
         </Card>
         <Card className="p-8 border-none shadow-sm bg-slate-900 text-white rounded-[2.5rem] relative overflow-hidden">
            <div className="absolute right-0 top-0 p-4 opacity-10">
               <FiAlertTriangle size={80} />
            </div>
            <p className="text-[10px] font-black text-brand-light uppercase tracking-widest mb-1">Impacto Financiero</p>
            <h3 className="text-2xl font-black italic">$4.2M</h3>
            <p className="mt-4 text-xs font-medium text-slate-400 leading-tight">Proyección de sobrecostos por reemplazos temporales este mes.</p>
         </Card>
      </div>

      <Card className="border-none shadow-sm overflow-hidden bg-white dark:bg-brand-deep/10 rounded-[2.5rem]">
         <CardHeader className="p-10 border-b border-slate-50 dark:border-white/5 bg-slate-50/50 dark:bg-black/20">
            <CardTitle className="font-black uppercase flex items-center gap-3 text-xl italic text-brand">
               <FiCalendar /> Bitácora de Novedades del Ciclo
            </CardTitle>
         </CardHeader>
         <CardContent className="p-0">
            <div className="divide-y divide-slate-50 dark:divide-white/5">
               {novelties.map((nov, i) => (
                  <div key={i} className="p-8 hover:bg-slate-50 dark:hover:bg-white/5 flex flex-col md:flex-row md:items-center justify-between gap-6 transition-all duration-300">
                     <div className="flex items-center gap-8">
                        <div className={`p-4 rounded-[1.25rem] ${nov.procesada ? 'bg-emerald-100 text-emerald-600' : 'bg-amber-100 text-amber-600'}`}>
                           {nov.procesada ? <FiCheckCircle size={24} /> : <FiClock size={24} />}
                        </div>
                        <div>
                           <div className="flex items-center gap-3 mb-1">
                              <Badge variant="outline" className="text-[9px] font-black uppercase px-3">{nov.concepto_detalle?.descripcion}</Badge>
                              <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest font-mono">{nov.fecha_evento}</span>
                           </div>
                           <p className="font-black text-xl text-slate-800 dark:text-white tracking-tight leading-none">
                              {nov.descripcion || 'Sin descripción pormenorizada'}
                           </p>
                           <p className="text-xs font-bold text-slate-400 mt-2">Valor Aplicado: <span className="text-slate-900 dark:text-slate-300">${Number(nov.valor).toLocaleString()}</span></p>
                        </div>
                     </div>
                     <div className="flex items-center gap-4">
                        <Badge className={nov.procesada ? 'bg-emerald-500 text-white font-black' : 'bg-amber-500 text-white font-black'}>
                           {nov.procesada ? 'PROCESADA' : 'EN COLA'}
                        </Badge>
                        <Button variant="ghost" className="text-brand font-black uppercase text-[10px] tracking-widest hover:bg-brand/5 px-6 py-3 rounded-xl transition-all">
                           Ver Evidencia <FiArrowRight className="ml-2" />
                        </Button>
                     </div>
                  </div>
               ))}
               {novelties.length === 0 && !isLoading && (
                  <div className="p-32 text-center text-slate-400 italic font-medium">
                     <FiAlertTriangle size={48} className="mx-auto mb-4 opacity-5" />
                     No se han reportado novedades en el ciclo operativo actual.
                  </div>
               )}
            </div>
         </CardContent>
      </Card>
    </div>
  );
}
