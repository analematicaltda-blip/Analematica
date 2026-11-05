'use client';

import React, { useEffect, useState } from 'react';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { FiPlus, FiFilter, FiDownload, FiDollarSign, FiArrowUp, FiArrowDown, FiChevronRight } from 'react-icons/fi';
import { Badge } from '@/components/ui/Badge';

export default function TesoreriaPage() {
  const { getTesoreria, getCashTransactions, isLoading } = useMiNegocioApi();
  const [data, setData] = useState<any>(null);
  const [transactions, setTransactions] = useState<any[]>([]);

  useEffect(() => {
    const load = async () => {
      const [t, txs] = await Promise.all([getTesoreria(), getCashTransactions()]);
      if (t && t.length > 0) setData(t[0]);
      if (txs) setTransactions(txs);
    };
    load();
  }, [getTesoreria, getCashTransactions]);

  return (
    <div className="space-y-8 py-8 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Caja y Tesorería</h1>
          <p className="text-slate-500 mt-1">Control de liquidez inmediata y administración de fondos.</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="font-bold border-slate-200"><FiDownload className="mr-2"/> Excel</Button>
          <Button className="bg-brand text-white font-black shadow-lg shadow-brand/20">
             <FiPlus className="mr-2"/> Registrar Movimiento
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-none shadow-sm bg-white p-8">
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-2">Disponible Operativo</p>
          <p className="text-4xl font-black text-slate-900">${data ? parseFloat(data.liquidez_disponible).toLocaleString() : '0.00'}</p>
          <div className="mt-4 flex items-center gap-2 text-xs font-bold text-green-500">
             <FiArrowUp /> <span>+12% vs mes anterior</span>
          </div>
        </Card>
        <Card className="border-none shadow-sm bg-white p-8">
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-2">Reservas de Capital</p>
          <p className="text-4xl font-black text-slate-900">${data ? parseFloat(data.reservas_totales).toLocaleString() : '0.00'}</p>
          <div className="mt-4 flex items-center gap-2 text-xs font-bold text-slate-400">
             <span>Objetivo: $10.0M</span>
          </div>
        </Card>
        <Card className="border-none shadow-sm bg-brand text-white p-8">
          <p className="text-[10px] font-black uppercase tracking-[0.2em] opacity-60 mb-2 text-white">Fondos en Custodia</p>
          <p className="text-4xl font-black">${data ? parseFloat(data.saldo_total_custodia).toLocaleString() : '0.00'}</p>
          <p className="text-xs mt-4 opacity-80 font-medium italic">Protegido por el GovernanceKernel</p>
        </Card>
      </div>

      <Card className="border-none shadow-sm overflow-hidden bg-white">
        <CardHeader className="p-8 border-b border-slate-50 flex flex-row items-center justify-between">
          <CardTitle className="text-xl font-black flex items-center gap-2 uppercase tracking-tighter">
            <FiDollarSign className="text-brand" /> Flujo de Caja Reciente
          </CardTitle>
          <Button variant="ghost" size="sm" className="text-slate-400 font-bold uppercase tracking-widest text-[10px]">
             <FiFilter className="mr-2" /> Filtrar Por Periodo
          </Button>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader className="bg-slate-50/50">
              <TableRow>
                <TableHead className="font-bold text-[10px] uppercase tracking-widest pl-8">Fecha</TableHead>
                <TableHead className="font-bold text-[10px] uppercase tracking-widest">Concepto / Referencia</TableHead>
                <TableHead className="font-bold text-[10px] uppercase tracking-widest">Beneficiario</TableHead>
                <TableHead className="text-right font-bold text-[10px] uppercase tracking-widest">Monto</TableHead>
                <TableHead className="font-bold text-[10px] uppercase tracking-widest">Estado</TableHead>
                <TableHead className="pr-8"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {transactions.map((tx: any) => (
                <TableRow key={tx.id} className="hover:bg-slate-50 transition-colors group">
                  <TableCell className="text-xs font-medium pl-8">{new Date(tx.fecha_pago).toLocaleDateString()}</TableCell>
                  <TableCell>
                     <div className="flex flex-col">
                        <span className="font-bold text-slate-800">{tx.concepto}</span>
                        <span className="text-[10px] font-mono text-slate-400">{tx.id.substring(0,8).toUpperCase()}</span>
                     </div>
                  </TableCell>
                  <TableCell className="text-xs font-bold text-slate-500">{tx.beneficiario_id ? tx.beneficiario_id.substring(0,8) : 'SISTEMA'}</TableCell>
                  <TableCell className="text-right">
                     <span className={`font-mono font-black text-lg ${parseFloat(tx.monto) < 0 ? 'text-red-500' : 'text-slate-900'}`}>
                        ${Math.abs(parseFloat(tx.monto)).toLocaleString()}
                     </span>
                  </TableCell>
                  <TableCell>
                    <Badge variant={tx.estado === 'PAGADA' ? 'default' : 'secondary'} className="text-[9px] font-black uppercase px-2 py-1">
                      {tx.estado}
                    </Badge>
                  </TableCell>
                  <TableCell className="pr-8 text-right">
                     <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100 transition-all">
                        <FiChevronRight />
                     </Button>
                  </TableCell>
                </TableRow>
              ))}
              {transactions.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-32 opacity-20">
                     <FiDollarSign size={64} className="mx-auto mb-4" />
                     <p className="text-xl font-black uppercase tracking-tighter">Sin movimientos registrados</p>
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
