'use client';

import React, { useEffect, useState } from 'react';
import { useMiNegocioApi } from '../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { FiPlus, FiCreditCard, FiArrowUpRight } from 'react-icons/fi';

export default function CreditosPage() {
  const { getCreditos, isLoading } = useMiNegocioApi();
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    const load = async () => {
      const res = await getCreditos();
      if (res) setData(res);
    };
    load();
  }, [getCreditos]);

  return (
    <div className="space-y-8 py-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Créditos y Financiación</h1>
          <p className="text-slate-500">Seguimiento de obligaciones financieras y tablas de amortización.</p>
        </div>
        <Button className="bg-brand text-white font-black"><FiPlus className="mr-2"/> Registrar Crédito</Button>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {data.map((c: any) => (
          <Card key={c.id} className="border-none shadow-sm bg-white overflow-hidden">
            <CardHeader className="p-8 border-b bg-slate-50/50 flex flex-row items-center justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                   <FiCreditCard className="text-brand" />
                   <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{c.entidad_financiera}</span>
                </div>
                <CardTitle className="text-2xl font-black">${parseFloat(c.monto_principal).toLocaleString()}</CardTitle>
              </div>
              <div className="flex gap-8">
                 <div className="text-right">
                    <p className="text-[10px] font-black text-slate-400 uppercase">Tasa Anual</p>
                    <p className="font-bold text-slate-900">{c.tasa_interes_anual}%</p>
                 </div>
                 <div className="text-right">
                    <p className="text-[10px] font-black text-slate-400 uppercase">Saldo Pendiente</p>
                    <p className="font-black text-red-500">${parseFloat(c.saldo_pendiente).toLocaleString()}</p>
                 </div>
              </div>
            </CardHeader>
            <CardContent className="p-0">
               <div className="p-6 bg-amber-50/30 border-b border-amber-50">
                  <p className="text-xs font-bold text-amber-700 flex items-center gap-2">
                     <FiArrowUpRight /> Próximo vencimiento: 15 de Octubre — $1,240,000
                  </p>
               </div>
               <Table>
                 <TableHeader>
                   <TableRow>
                     <TableHead># Cuota</TableHead>
                     <TableHead>Vencimiento</TableHead>
                     <TableHead className="text-right">Capital</TableHead>
                     <TableHead className="text-right">Interés</TableHead>
                     <TableHead className="text-right">Total</TableHead>
                     <TableHead>Estado</TableHead>
                   </TableRow>
                 </TableHeader>
                 <TableBody>
                   {c.cuotas?.map((q: any) => (
                     <TableRow key={q.id}>
                       <TableCell className="font-black text-slate-400">{q.numero_cuota}</TableCell>
                       <TableCell className="text-xs font-medium">{new Date(q.fecha_vencimiento).toLocaleDateString()}</TableCell>
                       <TableCell className="text-right font-mono">${parseFloat(q.monto_capital).toLocaleString()}</TableCell>
                       <TableCell className="text-right font-mono">${parseFloat(q.monto_interes).toLocaleString()}</TableCell>
                       <TableCell className="text-right font-mono font-black">${(parseFloat(q.monto_capital) + parseFloat(q.monto_interes)).toLocaleString()}</TableCell>
                       <TableCell>
                         <span className={`px-2 py-1 rounded-full text-[10px] font-black uppercase ${q.esta_pagada ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                           {q.esta_pagada ? 'Pagada' : 'Pendiente'}
                         </span>
                       </TableCell>
                     </TableRow>
                   ))}
                 </TableBody>
               </Table>
            </CardContent>
          </Card>
        ))}

        {data.length === 0 && (
           <div className="py-32 text-center opacity-20">
              <FiCreditCard size={64} className="mx-auto text-slate-400 mb-4" />
              <p className="text-xl font-black uppercase tracking-tighter">Sin obligaciones vigentes</p>
           </div>
        )}
      </div>
    </div>
  );
}
