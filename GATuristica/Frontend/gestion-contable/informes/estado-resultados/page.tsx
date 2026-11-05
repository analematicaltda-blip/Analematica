'use client';

import React, { useState, useEffect } from 'react';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';
import { Card, CardContent } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { FiDownload, FiArrowUpRight, FiArrowDownRight } from 'react-icons/fi';

export default function EstadoResultadosPage() {
  const { getEstadoResultados, isLoading } = useMiNegocioApi();
  const [report, setReport] = useState<any>(null);
  const [dateRange, setDateRange] = useState({
    inicio: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0],
    fin: new Date().toISOString().split('T')[0],
  });

  const loadData = async () => {
    const data = await getEstadoResultados(dateRange.inicio, dateRange.fin);
    if (data) setReport(data);
  };

  useEffect(() => {
    loadData();
  }, [getEstadoResultados]);

  if (!report) return null;

  return (
    <div className="space-y-8 py-8 max-w-4xl mx-auto">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Estado de Resultados</h1>
          <p className="text-slate-500 mt-1">Pérdidas y Ganancias acumuladas en el periodo.</p>
        </div>
        <Button variant="outline" size="sm"><FiDownload className="mr-2"/> Reporte Detallado</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
         <Card className="border-none shadow-sm bg-white p-6">
            <p className="text-[10px] font-black uppercase text-slate-400 mb-2">Ingresos Totales</p>
            <div className="flex items-center gap-2">
               <FiArrowUpRight className="text-green-500" />
               <p className="text-2xl font-black">${parseFloat(report.ingresos.total).toLocaleString()}</p>
            </div>
         </Card>
         <Card className="border-none shadow-sm bg-white p-6">
            <p className="text-[10px] font-black uppercase text-slate-400 mb-2">Gastos Totales</p>
            <div className="flex items-center gap-2">
               <FiArrowDownRight className="text-red-500" />
               <p className="text-2xl font-black">${parseFloat(report.gastos.total).toLocaleString()}</p>
            </div>
         </Card>
         <Card className={`border-none shadow-sm p-6 ${report.utilidad_neta >= 0 ? 'bg-brand text-white' : 'bg-red-500 text-white'}`}>
            <p className="text-[10px] font-black uppercase opacity-60 mb-2">Utilidad Neta</p>
            <p className="text-2xl font-black">${parseFloat(report.utilidad_neta).toLocaleString()}</p>
         </Card>
      </div>

      <div className="space-y-6">
         <Card className="border-none shadow-sm overflow-hidden">
            <div className="bg-slate-50 p-4 border-b font-bold text-xs uppercase tracking-widest text-slate-500">Desglose de Ingresos</div>
            <CardContent className="p-0">
               <Table>
                  <TableBody>
                     {report.ingresos.detalles.map((d: any, i: number) => (
                        <TableRow key={i}>
                           <TableCell className="font-bold">{d.cuenta}</TableCell>
                           <TableCell className="text-right font-mono font-bold text-green-600">+ ${parseFloat(d.valor).toLocaleString()}</TableCell>
                        </TableRow>
                     ))}
                  </TableBody>
               </Table>
            </CardContent>
         </Card>

         <Card className="border-none shadow-sm overflow-hidden">
            <div className="bg-slate-50 p-4 border-b font-bold text-xs uppercase tracking-widest text-slate-500">Desglose de Gastos</div>
            <CardContent className="p-0">
               <Table>
                  <TableBody>
                     {report.gastos.detalles.map((d: any, i: number) => (
                        <TableRow key={i}>
                           <TableCell className="font-bold">{d.cuenta}</TableCell>
                           <TableCell className="text-right font-mono font-bold text-red-500">- ${parseFloat(d.valor).toLocaleString()}</TableCell>
                        </TableRow>
                     ))}
                  </TableBody>
               </Table>
            </CardContent>
         </Card>
      </div>
    </div>
  );
}
