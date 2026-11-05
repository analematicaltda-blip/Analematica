'use client';

import React, { useEffect, useState } from 'react';
import { useMiNegocioApi, ChartOfAccount } from '../../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import {
  FiPlus,
  FiSearch,
  FiFilter,
  FiDownload,
  FiEdit2,
  FiTrash2,
  FiBook
} from 'react-icons/fi';
import { Badge } from '@/components/ui/Badge';

export default function PlanDeCuentasPage() {
  const { getChartOfAccounts, isLoading } = useMiNegocioApi();
  const [accounts, setAccounts] = useState<ChartOfAccount[]>([]);

  useEffect(() => {
    const loadAccounts = async () => {
      const data = await getChartOfAccounts();
      if (data) setAccounts(data);
    };
    loadAccounts();
  }, [getChartOfAccounts]);

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
           <div className="flex items-center gap-2 mb-1">
              <Link href="/dashboard/prestador/mi-negocio/gestion-contable" className="text-slate-400 hover:text-brand transition-colors font-bold text-xs uppercase tracking-widest">Contabilidad</Link>
              <span className="text-slate-300">/</span>
              <span className="text-brand font-black text-xs uppercase tracking-widest">Plan de Cuentas</span>
           </div>
          <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Estructura del Plan Maestro</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1 text-sm">Catálogo estandarizado para el registro de hechos económicos.</p>
        </div>
        <div className="flex gap-3">
           <Button variant="outline" className="border-slate-200 dark:border-white/5 font-bold">
              <FiDownload className="mr-2" /> Exportar
           </Button>
           <Button className="bg-brand hover:bg-brand-light text-white font-black px-6 shadow-lg shadow-brand/20 transition-all">
              <FiPlus className="mr-2" /> Crear Cuenta
           </Button>
        </div>
      </div>

      {/* Toolbar */}
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between bg-white dark:bg-brand-deep/20 p-4 rounded-2xl shadow-sm border border-slate-50 dark:border-white/5">
         <div className="relative flex-1 w-full max-w-md">
            <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Buscar por código o nombre de cuenta..."
              className="w-full pl-12 pr-4 py-3 bg-slate-50 dark:bg-black/20 border border-transparent focus:border-brand/30 rounded-xl text-sm outline-none transition-all"
            />
         </div>
         <div className="flex gap-2">
            <Button variant="ghost" size="sm" className="text-slate-500 hover:text-brand font-bold uppercase tracking-tighter text-[10px]">
               <FiFilter className="mr-2" /> Filtros Avanzados
            </Button>
         </div>
      </div>

      <Card className="border-none shadow-sm overflow-hidden bg-white dark:bg-brand-deep/10">
         <CardContent className="p-0">
            <Table>
               <TableHeader className="bg-slate-50 dark:bg-black/40 border-b border-slate-100 dark:border-white/5">
                  <TableRow>
                     <TableHead className="font-black text-[10px] uppercase tracking-widest w-[120px]">Código</TableHead>
                     <TableHead className="font-black text-[10px] uppercase tracking-widest">Nombre de la Cuenta</TableHead>
                     <TableHead className="font-black text-[10px] uppercase tracking-widest">Naturaleza</TableHead>
                     <TableHead className="font-black text-[10px] uppercase tracking-widest">Tipo</TableHead>
                     <TableHead className="font-black text-[10px] uppercase tracking-widest text-right">Saldo Actual</TableHead>
                     <TableHead className="font-black text-[10px] uppercase tracking-widest text-right">Acciones</TableHead>
                  </TableRow>
               </TableHeader>
               <TableBody>
                  {accounts.map((acc) => (
                    <TableRow key={acc.code} className="hover:bg-slate-50 dark:hover:bg-white/5 transition-colors border-slate-50 dark:border-white/5">
                       <TableCell className="font-mono text-xs font-black text-brand">{acc.code}</TableCell>
                       <TableCell className="font-bold text-slate-700 dark:text-slate-200">{acc.name}</TableCell>
                       <TableCell>
                          <Badge variant={acc.nature === 'DEBITO' ? 'default' : 'secondary'} className="text-[9px] font-black uppercase tracking-tighter px-2">
                             {acc.nature}
                          </Badge>
                       </TableCell>
                       <TableCell className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Auxiliar</TableCell>
                       <TableCell className="text-right font-black text-slate-900 dark:text-white">$0.00</TableCell>
                       <TableCell className="text-right">
                          <div className="flex justify-end gap-1">
                             <Button variant="ghost" size="sm" className="h-8 w-8 p-0 hover:text-brand"><FiEdit2 size={14} /></Button>
                             <Button variant="ghost" size="sm" className="h-8 w-8 p-0 hover:text-red-500"><FiTrash2 size={14} /></Button>
                          </div>
                       </TableCell>
                    </TableRow>
                  ))}
                  {accounts.length === 0 && !isLoading && (
                    <TableRow>
                       <TableCell colSpan={6} className="text-center py-32">
                          <div className="flex flex-col items-center opacity-20">
                             <FiBook size={64} className="text-slate-400" />
                             <p className="mt-4 font-black text-xl text-slate-500">Plan de cuentas vacío</p>
                             <p className="text-sm">Configura tu catálogo maestro para comenzar.</p>
                          </div>
                       </TableCell>
                    </TableRow>
                  )}
                  {isLoading && (
                    [...Array(5)].map((_, i) => (
                       <TableRow key={i}>
                          <TableCell colSpan={6}><div className="h-10 bg-slate-50 dark:bg-white/5 rounded-lg animate-pulse" /></TableCell>
                       </TableRow>
                    ))
                  )}
               </TableBody>
            </Table>
         </CardContent>
      </Card>
    </div>
  );
}

import Link from 'next/link';
