'use client';

import React, { useState, useEffect } from 'react';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';
import { Card, CardContent } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { FiDownload, FiSearch } from 'react-icons/fi';

export default function LibroMayorPage() {
  const { getLibroMayor, getChartOfAccounts, isLoading } = useMiNegocioApi();
  const [accounts, setAccounts] = useState<any[]>([]);
  const [movements, setMovements] = useState<any[]>([]);
  const [filters, setFilters] = useState({
    cuenta_codigo: '',
    inicio: new Date(new Date().getFullYear(), 0, 1).toISOString().split('T')[0],
    fin: new Date().toISOString().split('T')[0],
  });

  useEffect(() => {
    const loadAccounts = async () => {
      const data = await getChartOfAccounts();
      if (data) setAccounts(data);
    };
    loadAccounts();
  }, [getChartOfAccounts]);

  const handleSearch = async () => {
    if (!filters.cuenta_codigo) return;
    const data = await getLibroMayor(filters.cuenta_codigo, filters.inicio, filters.fin);
    if (data) setMovements(data);
  };

  return (
    <div className="space-y-8 py-8">
      <div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Libro Mayor</h1>
        <p className="text-slate-500 mt-1">Movimientos históricos filtrados por cuenta contable.</p>
      </div>

      <Card className="border-none shadow-sm p-6 bg-white">
         <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
            <div className="space-y-1">
               <label className="text-[10px] font-black uppercase text-slate-400">Seleccionar Cuenta</label>
               <select
                  value={filters.cuenta_codigo}
                  onChange={(e) => setFilters({...filters, cuenta_codigo: e.target.value})}
                  className="w-full p-2 bg-slate-50 rounded-lg text-sm border-none outline-none font-bold"
               >
                  <option value="">Seleccione...</option>
                  {accounts.map(acc => (
                     <option key={acc.code} value={acc.code}>{acc.code} - {acc.name}</option>
                  ))}
               </select>
            </div>
            <div className="space-y-1">
               <label className="text-[10px] font-black uppercase text-slate-400">Desde</label>
               <input
                  type="date"
                  value={filters.inicio}
                  onChange={(e) => setFilters({...filters, inicio: e.target.value})}
                  className="w-full p-2 bg-slate-50 rounded-lg text-sm border-none outline-none"
               />
            </div>
            <div className="space-y-1">
               <label className="text-[10px] font-black uppercase text-slate-400">Hasta</label>
               <input
                  type="date"
                  value={filters.fin}
                  onChange={(e) => setFilters({...filters, fin: e.target.value})}
                  className="w-full p-2 bg-slate-50 rounded-lg text-sm border-none outline-none"
               />
            </div>
            <Button onClick={handleSearch} className="bg-brand text-white font-black h-[40px] shadow-lg shadow-brand/20">
               <FiSearch className="mr-2" /> Consultar
            </Button>
         </div>
      </Card>

      <Card className="border-none shadow-sm overflow-hidden bg-white">
         <CardContent className="p-0">
            <Table>
               <TableHeader className="bg-slate-50 border-b">
                  <TableRow>
                     <TableHead className="font-bold text-[10px] uppercase tracking-widest">Fecha</TableHead>
                     <TableHead className="font-bold text-[10px] uppercase tracking-widest">Comprobante</TableHead>
                     <TableHead className="font-bold text-[10px] uppercase tracking-widest">Detalle</TableHead>
                     <TableHead className="font-bold text-[10px] uppercase tracking-widest text-right">Débito</TableHead>
                     <TableHead className="font-bold text-[10px] uppercase tracking-widest text-right">Crédito</TableHead>
                  </TableRow>
               </TableHeader>
               <TableBody>
                  {movements.map((m: any) => (
                     <TableRow key={m.id}>
                        <TableCell className="text-xs font-medium">{new Date(m.asiento.fecha).toLocaleDateString()}</TableCell>
                        <TableCell className="text-xs font-black text-brand">#{m.asiento.id.substring(0,8)}</TableCell>
                        <TableCell className="text-xs text-slate-600">{m.descripcion || m.asiento.descripcion}</TableCell>
                        <TableCell className="text-right font-mono font-bold">{m.debito > 0 ? `$${parseFloat(m.debito).toLocaleString()}` : '-'}</TableCell>
                        <TableCell className="text-right font-mono font-bold">{m.credito > 0 ? `$${parseFloat(m.credito).toLocaleString()}` : '-'}</TableCell>
                     </TableRow>
                  ))}
                  {movements.length === 0 && (
                     <TableRow>
                        <TableCell colSpan={5} className="py-24 text-center opacity-30 italic">
                           No hay movimientos para mostrar. Seleccione una cuenta y rango de fechas.
                        </TableCell>
                     </TableRow>
                  )}
               </TableBody>
            </Table>
         </CardContent>
      </Card>
    </div>
  );
}
