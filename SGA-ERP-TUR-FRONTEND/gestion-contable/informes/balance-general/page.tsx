'use client';

import React, { useState, useEffect } from 'react';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { FiDownload, FiPrinter } from 'react-icons/fi';

export default function BalanceGeneralPage() {
  const { getBalanceGeneral, isLoading } = useMiNegocioApi();
  const [report, setReport] = useState<any>(null);
  const [corte, setCorte] = useState(new Date().toISOString().split('T')[0]);

  const loadData = async () => {
    const data = await getBalanceGeneral(corte);
    if (data) setReport(data);
  };

  useEffect(() => {
    loadData();
  }, [getBalanceGeneral]);

  if (!report) return null;

  return (
    <div className="space-y-8 py-8 max-w-4xl mx-auto">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Balance General</h1>
          <p className="text-slate-500 mt-1">Estado de situación financiera a una fecha de corte.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm"><FiDownload className="mr-2"/> PDF</Button>
          <Button variant="outline" size="sm"><FiPrinter className="mr-2"/> Imprimir</Button>
        </div>
      </div>

      <div className="bg-white p-4 rounded-xl shadow-sm border flex items-center justify-between">
         <div className="flex items-center gap-4">
            <label className="text-[10px] font-black uppercase text-slate-400 tracking-widest">Corte al:</label>
            <input
               type="date"
               value={corte}
               onChange={(e) => setCorte(e.target.value)}
               className="p-2 bg-slate-50 rounded-lg text-sm border-none outline-none font-bold"
            />
            <Button onClick={loadData} size="sm" className="bg-brand text-white">Actualizar</Button>
         </div>
         <div className="text-right">
            <span className="text-[10px] font-black uppercase text-slate-400">Diferencia Ecuación:</span>
            <p className={`font-mono font-bold ${report.diferencia_ecuacion == 0 ? 'text-green-600' : 'text-red-500'}`}>
               ${parseFloat(report.diferencia_ecuacion).toLocaleString()}
            </p>
         </div>
      </div>

      {['ACTIVO', 'PASIVO', 'PATRIMONIO'].map((seccion) => (
         <Card key={seccion} className="border-none shadow-sm overflow-hidden">
            <div className="bg-slate-900 text-white p-4 font-black uppercase tracking-[0.2em] text-xs">
               {seccion}
            </div>
            <CardContent className="p-0">
               <Table>
                  <TableHeader className="hidden">
                     <TableRow>
                        <TableHead>Cuenta</TableHead>
                        <TableHead className="text-right">Saldo</TableHead>
                     </TableRow>
                  </TableHeader>
                  <TableBody>
                     {report.balance[seccion]?.map((cuenta: any) => (
                        <TableRow key={cuenta.codigo} className="border-slate-50">
                           <TableCell className="py-4">
                              <div className="flex items-baseline gap-4">
                                 <span className="font-mono text-xs text-slate-400 w-16">{cuenta.codigo}</span>
                                 <span className="font-bold text-slate-700">{cuenta.cuenta}</span>
                              </div>
                           </TableCell>
                           <TableCell className="text-right font-mono font-black text-slate-900">
                              ${parseFloat(cuenta.saldo).toLocaleString()}
                           </TableCell>
                        </TableRow>
                     ))}
                     <TableRow className="bg-slate-50/50">
                        <TableCell className="font-black text-xs uppercase text-slate-400 tracking-widest">Total {seccion}</TableCell>
                        <TableCell className="text-right font-mono font-black text-lg text-brand">
                           ${parseFloat(report.totales[seccion]).toLocaleString()}
                        </TableCell>
                     </TableRow>
                  </TableBody>
               </Table>
            </CardContent>
         </Card>
      ))}

      <div className="bg-brand-deep text-white p-8 rounded-3xl shadow-xl flex justify-between items-center">
         <div>
            <p className="text-xs font-bold uppercase tracking-[0.3em] opacity-50 mb-2">Pasivo + Patrimonio</p>
            <p className="text-4xl font-black">${(parseFloat(report.totales['PASIVO']) + parseFloat(report.totales['PATRIMONIO'])).toLocaleString()}</p>
         </div>
         <div className="h-12 w-[2px] bg-white/10" />
         <div className="text-right">
            <p className="text-xs font-bold uppercase tracking-[0.3em] opacity-50 mb-2 text-brand-light">Activo Total</p>
            <p className="text-4xl font-black text-brand-light">${parseFloat(report.totales['ACTIVO']).toLocaleString()}</p>
         </div>
      </div>
    </div>
  );
}
