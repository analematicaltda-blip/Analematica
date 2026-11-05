'use client';

import React, { useState, useEffect } from 'react';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';
import { Card, CardContent } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { FiDownload, FiFilter, FiPrinter } from 'react-icons/fi';

export default function LibroDiarioPage() {
  const { getLibroDiario, isLoading } = useMiNegocioApi();
  const [entries, setEntries] = useState<any[]>([]);
  const [dateRange, setDateRange] = useState({
    inicio: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0],
    fin: new Date().toISOString().split('T')[0],
  });

  const loadData = async () => {
    const data = await getLibroDiario(dateRange.inicio, dateRange.fin);
    if (data) setEntries(data);
  };

  useEffect(() => {
    loadData();
  }, [getLibroDiario]);

  return (
    <div className="space-y-8 py-8">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Libro Diario</h1>
          <p className="text-slate-500 mt-1">Registros cronológicos detallados por partida doble.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm"><FiDownload className="mr-2"/> Excel</Button>
          <Button variant="outline" size="sm"><FiPrinter className="mr-2"/> Imprimir</Button>
        </div>
      </div>

      <Card className="border-none shadow-sm p-4 bg-white">
        <div className="flex gap-4 items-end">
          <div className="space-y-1">
            <label className="text-[10px] font-black uppercase text-slate-400">Fecha Inicio</label>
            <input
              type="date"
              value={dateRange.inicio}
              onChange={(e) => setDateRange({...dateRange, inicio: e.target.value})}
              className="block p-2 bg-slate-50 rounded-lg text-sm border-none outline-none focus:ring-1 ring-brand/30"
            />
          </div>
          <div className="space-y-1">
            <label className="text-[10px] font-black uppercase text-slate-400">Fecha Fin</label>
            <input
              type="date"
              value={dateRange.fin}
              onChange={(e) => setDateRange({...dateRange, fin: e.target.value})}
              className="block p-2 bg-slate-50 rounded-lg text-sm border-none outline-none focus:ring-1 ring-brand/30"
            />
          </div>
          <Button onClick={loadData} className="bg-slate-900 text-white font-bold px-6 h-[38px]"><FiFilter className="mr-2"/> Filtrar</Button>
        </div>
      </Card>

      <div className="space-y-4">
        {entries.map((asiento: any) => (
          <Card key={asiento.id} className="border-none shadow-sm overflow-hidden">
            <div className="bg-slate-50 p-4 border-b border-slate-100 flex justify-between items-center">
              <div className="flex gap-4 items-center">
                <span className="font-black text-brand text-xs uppercase tracking-widest">#{asiento.id.substring(0,8)}</span>
                <span className="text-sm font-bold text-slate-600">{new Date(asiento.fecha).toLocaleDateString()}</span>
                <span className="text-sm text-slate-500 font-medium">— {asiento.descripcion}</span>
              </div>
              <span className="text-[10px] font-black text-slate-400 uppercase">Registrado por: {asiento.creado_por}</span>
            </div>
            <CardContent className="p-0">
              <Table>
                <TableHeader className="hidden">
                  <TableRow>
                    <TableHead>Cuenta</TableHead>
                    <TableHead>Descripción</TableHead>
                    <TableHead className="text-right">Débito</TableHead>
                    <TableHead className="text-right">Crédito</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {asiento.transacciones.map((tx: any) => (
                    <TableRow key={tx.id} className="border-none">
                      <TableCell className="w-[300px]">
                        <div className="flex flex-col">
                          <span className="text-[10px] font-black text-brand-deep/50">{tx.cuenta.codigo}</span>
                          <span className="text-sm font-bold">{tx.cuenta.nombre}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-slate-500 text-xs italic">{tx.descripcion}</TableCell>
                      <TableCell className="text-right font-mono font-bold text-slate-900">{tx.debito > 0 ? `$${parseFloat(tx.debito).toLocaleString()}` : '-'}</TableCell>
                      <TableCell className="text-right font-mono font-bold text-slate-900">{tx.credito > 0 ? `$${parseFloat(tx.credito).toLocaleString()}` : '-'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        ))}

        {entries.length === 0 && !isLoading && (
          <div className="py-32 text-center opacity-30">
            <p className="text-xl font-black">No se encontraron movimientos</p>
          </div>
        )}
      </div>
    </div>
  );
}
