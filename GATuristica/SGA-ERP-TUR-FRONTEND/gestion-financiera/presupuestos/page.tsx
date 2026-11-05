'use client';

import React, { useEffect, useState } from 'react';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { FiPlus, FiTarget, FiFilter, FiDownload, FiActivity, FiArrowRight } from 'react-icons/fi';
import { Badge } from '@/components/ui/Badge';

export default function PresupuestosPage() {
  const { getPresupuestos, isLoading } = useMiNegocioApi();
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    const load = async () => {
      const res = await getPresupuestos();
      if (res) setData(res);
    };
    load();
  }, [getPresupuestos]);

  return (
    <div className="space-y-8 py-8 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight tracking-tighter">Gobierno Presupuestal</h1>
          <p className="text-slate-500 mt-1">Planificación estratégica y control de ejecución por centro de costo.</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="font-bold border-slate-200 shadow-sm"><FiDownload className="mr-2"/> Reporte Varianza</Button>
          <Button className="bg-brand hover:bg-brand-light text-white font-black px-8 rounded-xl shadow-lg shadow-brand/20 transition-all">
             <FiPlus className="mr-2"/> Definir Presupuesto
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-8">
        {data.map((p: any) => {
          const totalEst = parseFloat(p.total_estimado) || 1;
          const totalEjec = parseFloat(p.total_ejecutado) || 0;
          const progress = (totalEjec / totalEst) * 100;

          return (
            <Card key={p.id} className="border-none shadow-sm overflow-hidden bg-white hover:shadow-xl transition-all duration-300">
              <CardHeader className="p-8 border-b bg-slate-50/50 flex flex-col md:flex-row items-center justify-between gap-6">
                <div className="flex items-center gap-6">
                   <div className="w-16 h-16 bg-white rounded-2xl shadow-sm flex items-center justify-center text-brand">
                      <FiTarget size={32} />
                   </div>
                   <div>
                      <CardTitle className="text-2xl font-black">{p.nombre}</CardTitle>
                      <div className="flex gap-4 mt-1">
                         <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Año: {p.año}</span>
                         <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">CC: {p.centro_costo || 'GENERAL'}</span>
                      </div>
                   </div>
                </div>
                <div className="text-right space-y-1">
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Ejecución Global</p>
                  <p className={`text-3xl font-black ${progress > 90 ? 'text-red-500' : 'text-brand'}`}>{progress.toFixed(1)}%</p>
                </div>
              </CardHeader>
              <CardContent className="p-8">
                <div className="space-y-10">
                   {/* Progress Bar Premium */}
                   <div className="space-y-3">
                      <div className="flex justify-between text-xs font-bold uppercase tracking-widest text-slate-500">
                         <span>Consumo de Recursos</span>
                         <span>${totalEjec.toLocaleString()} / ${totalEst.toLocaleString()}</span>
                      </div>
                      <div className="h-4 bg-slate-100 rounded-full overflow-hidden shadow-inner border border-slate-50">
                         <div
                           style={{ width: `${Math.min(progress, 100)}%` }}
                           className={`h-full transition-all duration-1000 ${progress > 95 ? 'bg-red-500' : progress > 80 ? 'bg-amber-500' : 'bg-brand'}`}
                         />
                      </div>
                   </div>

                   <Table>
                     <TableHeader className="bg-slate-50/50">
                       <TableRow>
                         <TableHead className="font-black text-[10px] uppercase tracking-widest pl-6">Rubro Contable</TableHead>
                         <TableHead className="text-right font-black text-[10px] uppercase tracking-widest">Asignado</TableHead>
                         <TableHead className="text-right font-black text-[10px] uppercase tracking-widest">Ejecutado</TableHead>
                         <TableHead className="text-right font-black text-[10px] uppercase tracking-widest">Saldo</TableHead>
                         <TableHead className="pr-6"></TableHead>
                       </TableRow>
                     </TableHeader>
                     <TableBody>
                       {p.lineas?.map((l: any) => {
                          const rubroSaldo = parseFloat(l.monto_presupuestado) - parseFloat(l.monto_ejecutado);
                          return (
                            <TableRow key={l.id} className="hover:bg-slate-50 transition-colors group">
                              <TableCell className="font-bold text-slate-700 pl-6">{l.nombre_item}</TableCell>
                              <TableCell className="text-right font-mono font-medium">${parseFloat(l.monto_presupuestado).toLocaleString()}</TableCell>
                              <TableCell className="text-right font-mono font-bold text-red-500">-${parseFloat(l.monto_ejecutado).toLocaleString()}</TableCell>
                              <TableCell className="text-right font-mono font-black text-slate-900">${rubroSaldo.toLocaleString()}</TableCell>
                              <TableCell className="pr-6 text-right">
                                 <Button variant="ghost" size="sm" className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100"><FiArrowRight /></Button>
                              </TableCell>
                            </TableRow>
                          );
                       })}
                     </TableBody>
                   </Table>
                </div>
              </CardContent>
            </Card>
          );
        })}

        {data.length === 0 && (
           <div className="py-40 text-center bg-white rounded-[2rem] shadow-sm border-2 border-dashed border-slate-100 flex flex-col items-center">
              <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center text-slate-200 mb-6">
                 <FiTarget size={40} />
              </div>
              <p className="text-2xl font-black text-slate-300 uppercase tracking-tighter">Sin presupuestos definidos</p>
              <p className="text-slate-400 mt-2 max-w-xs mx-auto">Comience a planificar sus recursos financieros para un mejor control de gobierno.</p>
              <Button className="mt-8 bg-brand text-white font-black px-10">Crear Primer Presupuesto</Button>
           </div>
        )}
      </div>
    </div>
  );
}
