'use client';
import React, { useEffect, useState } from 'react';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { FiSearch, FiCheckSquare, FiPlus, FiMapPin, FiArrowRight } from 'react-icons/fi';

export default function InspeccionesPage() {
  const { getSSTInspecciones, isLoading } = useMiNegocioApi();
  const [inspections, setInspections] = useState<any[]>([]);

  useEffect(() => {
    getSSTInspecciones().then(res => res && setInspections(res));
  }, [getSSTInspecciones]);

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 className="text-3xl font-black uppercase italic text-slate-900 dark:text-white leading-tight">Inspecciones Internas</h1>
          <p className="text-slate-500">Verificación proactiva de condiciones de seguridad, orden y aseo en centros de trabajo.</p>
        </div>
        <Button className="bg-brand hover:bg-brand-deep text-white font-black px-8 h-14 rounded-2xl shadow-xl shadow-brand/20 transition-all">
          <FiPlus className="mr-2" /> Programar Inspección
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
        {inspections.map((ins, i) => (
          <Card key={i} className="border-none shadow-sm p-10 bg-white dark:bg-brand-deep/10 rounded-[2.5rem] group transition-all hover:ring-2 hover:ring-brand relative overflow-hidden">
             <div className="absolute top-0 right-0 p-10 opacity-[0.03] group-hover:scale-110 transition-transform text-brand">
                <FiCheckSquare size={180} />
             </div>

             <div className="flex justify-between items-start mb-8 relative z-10">
                <div>
                   <Badge className="bg-indigo-500 text-white font-black mb-4 px-4 py-1 rounded-lg shadow-sm">{ins.tipo}</Badge>
                   <h3 className="text-3xl font-black text-slate-800 dark:text-white tracking-tighter italic">REPORTE DE HALLAZGOS</h3>
                   <p className="flex items-center gap-2 text-slate-500 font-black text-[10px] uppercase tracking-[0.2em] mt-3">
                      <FiMapPin className="text-brand" /> {ins.centro_trabajo}
                   </p>
                </div>
                <div className="text-right">
                   <p className="text-[10px] font-black text-slate-400 uppercase mb-1 font-mono">Índice de Cierre</p>
                   <p className="text-4xl font-black text-emerald-500 font-mono tracking-tighter">{ins.porcentaje_hallazgos_cerrados}%</p>
                </div>
             </div>

             <div className="space-y-4 mb-10 relative z-10">
                {ins.hallazgos && ins.hallazgos.length > 0 ? (
                   ins.hallazgos.slice(0, 3).map((h: any, j: number) => (
                      <div key={j} className="flex items-center gap-4 p-5 bg-slate-50/80 dark:bg-black/40 rounded-2xl backdrop-blur-sm border border-slate-100 dark:border-white/5">
                         <div className={`w-3 h-3 rounded-full shadow-sm ${h.cerrado ? 'bg-emerald-500' : 'bg-red-500 animate-pulse'}`} />
                         <p className="text-sm font-black text-slate-700 dark:text-slate-300 flex-1 line-clamp-1">{h.descripcion}</p>
                         <Badge variant="outline" className="text-[8px] font-black uppercase bg-white dark:bg-black/20">{h.criticidad}</Badge>
                      </div>
                   ))
                ) : (
                   <div className="p-10 text-center bg-emerald-50/30 dark:bg-emerald-950/10 rounded-2xl border border-emerald-100 dark:border-emerald-900/30">
                      <p className="text-emerald-600 dark:text-emerald-400 font-black text-xs uppercase tracking-widest">Sin hallazgos pendientes. Condición Óptima.</p>
                   </div>
                )}
                {ins.hallazgos?.length > 3 && (
                   <p className="text-[10px] font-bold text-slate-400 text-center italic">+{ins.hallazgos.length - 3} hallazgos adicionales registrados</p>
                )}
             </div>

             <div className="flex justify-between items-center relative z-10 border-t border-slate-50 dark:border-white/5 pt-6">
                <div className="flex flex-col">
                   <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Fecha Inspección</span>
                   <span className="text-xs font-bold text-slate-600 dark:text-slate-400">{new Date(ins.fecha).toLocaleDateString('es-CO', { day: '2-digit', month: 'long', year: 'numeric' })}</span>
                </div>
                <Button className="bg-slate-900 dark:bg-brand text-white font-black uppercase text-[10px] tracking-widest px-8 py-3 rounded-xl shadow-lg group-hover:px-10 transition-all">
                   Ver Detalles <FiArrowRight className="ml-2" />
                </Button>
             </div>
          </Card>
        ))}
        {inspections.length === 0 && !isLoading && (
           <div className="col-span-full p-40 text-center border-2 border-dashed border-slate-200 dark:border-white/5 rounded-[4rem] bg-white/30 dark:bg-transparent">
              <FiSearch size={80} className="mx-auto mb-6 opacity-5" />
              <p className="text-slate-400 text-lg font-black uppercase italic tracking-widest">Protocolo de Inspección Inactivo</p>
              <p className="text-slate-400 text-sm mt-2 max-w-sm mx-auto">No se han detectado reportes de inspección en los últimos ciclos operativos.</p>
              <Button variant="outline" className="mt-8 font-black uppercase text-xs tracking-widest px-10 h-12 border-slate-200">Generar Checklist de Emergencia</Button>
           </div>
        )}
      </div>
    </div>
  );
}
