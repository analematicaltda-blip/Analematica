'use client';

import React, { useEffect, useState } from 'react';
import { useMiNegocioApi, JournalEntry } from '../../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import {
  FiPlus,
  FiSearch,
  FiCalendar,
  FiFileText,
  FiActivity,
  FiChevronRight
} from 'react-icons/fi';
import { Badge } from '@/components/ui/Badge';
import Link from 'next/link';

export default function AsientosContablesPage() {
  const { getJournalEntries, isLoading } = useMiNegocioApi();
  const [entries, setEntries] = useState<JournalEntry[]>([]);

  useEffect(() => {
    const loadEntries = async () => {
      const data = await getJournalEntries();
      if (data) setEntries(data);
    };
    loadEntries();
  }, [getJournalEntries]);

  return (
    <div className="space-y-8 animate-in slide-in-from-right-4 duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
           <div className="flex items-center gap-2 mb-1">
              <Link href="/dashboard/prestador/mi-negocio/gestion-contable" className="text-slate-400 hover:text-brand transition-colors font-bold text-xs uppercase tracking-widest">Contabilidad</Link>
              <span className="text-slate-300">/</span>
              <span className="text-brand font-black text-xs uppercase tracking-widest">Libro Diario</span>
           </div>
          <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Registro de Asientos Contables</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1 text-sm">Cronología detallada de los hechos económicos del negocio.</p>
        </div>
        <Link href="/dashboard/prestador/mi-negocio/gestion-contable/asientos/nuevo">
           <Button className="bg-brand hover:bg-brand-light text-white font-black px-8 py-6 rounded-2xl shadow-lg shadow-brand/20 transition-all">
              <FiPlus className="mr-2" /> Nuevo Asiento Manual
           </Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
         <Card className="lg:col-span-2 border-none shadow-sm overflow-hidden bg-white dark:bg-brand-deep/10">
            <CardHeader className="p-6 border-b border-slate-50 dark:border-white/5 flex flex-row items-center justify-between">
               <CardTitle className="text-lg font-bold">Últimos Registros</CardTitle>
               <div className="flex gap-4">
                  <div className="relative">
                     <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                     <input type="text" placeholder="Buscar..." className="pl-9 pr-4 py-2 bg-slate-50 dark:bg-black/20 border-none rounded-lg text-xs" />
                  </div>
               </div>
            </CardHeader>
            <CardContent className="p-0">
               <Table>
                  <TableHeader className="bg-slate-50/50 dark:bg-black/20">
                     <TableRow>
                        <TableHead className="font-bold text-[10px] uppercase tracking-widest">ID / Fecha</TableHead>
                        <TableHead className="font-bold text-[10px] uppercase tracking-widest">Descripción</TableHead>
                        <TableHead className="font-bold text-[10px] uppercase tracking-widest">Tipo</TableHead>
                        <TableHead className="font-bold text-[10px] uppercase tracking-widest text-right">Valor</TableHead>
                        <TableHead className="font-bold text-[10px] uppercase tracking-widest text-right"></TableHead>
                     </TableRow>
                  </TableHeader>
                  <TableBody>
                     {entries.map((entry) => (
                       <TableRow key={entry.id} className="hover:bg-slate-50 dark:hover:bg-white/5 transition-colors border-slate-50 dark:border-white/5 group">
                          <TableCell>
                             <div className="flex flex-col leading-tight">
                                <span className="font-black text-xs text-brand">#{entry.id}</span>
                                <span className="text-[10px] text-slate-400 font-bold uppercase">{new Date(entry.entry_date).toLocaleDateString()}</span>
                             </div>
                          </TableCell>
                          <TableCell>
                             <p className="text-sm font-bold text-slate-700 dark:text-slate-200 line-clamp-1">{entry.description}</p>
                          </TableCell>
                          <TableCell>
                             <Badge variant="outline" className="text-[9px] font-black uppercase tracking-tighter border-slate-200 dark:border-white/10 text-slate-500">
                                {entry.entry_type}
                             </Badge>
                          </TableCell>
                          <TableCell className="text-right font-black text-slate-900 dark:text-white">$0.00</TableCell>
                          <TableCell className="text-right">
                             <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100 transition-opacity">
                                <FiChevronRight />
                             </Button>
                          </TableCell>
                       </TableRow>
                     ))}
                     {entries.length === 0 && !isLoading && (
                        <TableRow>
                           <TableCell colSpan={5} className="py-24 text-center">
                              <div className="flex flex-col items-center opacity-20">
                                 <FiActivity size={48} className="text-slate-400" />
                                 <p className="mt-4 font-black">Libro diario sin registros</p>
                              </div>
                           </TableCell>
                        </TableRow>
                     )}
                  </TableBody>
               </Table>
            </CardContent>
         </Card>

         {/* Resumen Fiscal */}
         <div className="space-y-6">
            <Card className="border-none shadow-sm bg-slate-900 text-white p-8">
               <h3 className="text-lg font-black uppercase tracking-[0.2em] text-brand-light mb-6">Estado de Cierre</h3>
               <div className="space-y-8">
                  <div className="flex items-center gap-4">
                     <div className="w-12 h-12 bg-white/5 rounded-2xl flex items-center justify-center text-brand-light">
                        <FiCalendar size={24} />
                     </div>
                     <div>
                        <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Periodo Actual</p>
                        <p className="text-lg font-black uppercase">Agosto 2024</p>
                     </div>
                  </div>
                  <div className="bg-white/5 p-6 rounded-2xl border border-white/5">
                     <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Progreso del Cierre</p>
                     <div className="h-2 bg-white/10 rounded-full overflow-hidden mb-4">
                        <div className="h-full bg-brand w-[12%] shadow-[0_0_15px_rgba(0,109,91,0.5)]" />
                     </div>
                     <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Aún faltan conciliaciones bancarias.</p>
                  </div>
                  <Button className="w-full bg-brand hover:bg-brand-light font-black py-4 rounded-xl transition-all">
                     Pre-visualizar Balance
                  </Button>
               </div>
            </Card>

            <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8">
               <div className="flex items-center gap-2 mb-4">
                  <FiFileText className="text-brand" />
                  <h4 className="font-bold text-slate-900 dark:text-white uppercase tracking-tighter">Certificaciones</h4>
               </div>
               <p className="text-sm text-slate-500 mb-6 leading-relaxed">Genera automáticamente tus certificados de retención y estados financieros.</p>
               <div className="space-y-2">
                  <Button variant="outline" className="w-full justify-start text-xs font-bold border-slate-100 dark:border-white/5 hover:bg-slate-50 dark:hover:bg-black/20">Estado de Situación Financiera</Button>
                  <Button variant="outline" className="w-full justify-start text-xs font-bold border-slate-100 dark:border-white/5 hover:bg-slate-50 dark:hover:bg-black/20">Estado de Resultados Integral</Button>
               </div>
            </Card>
         </div>
      </div>
    </div>
  );
}
