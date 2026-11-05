'use client';

import React from 'react';
import Link from 'next/link';
import { useComercialApi } from './hooks/useComercialApi';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import {
  FiPlus,
  FiDollarSign,
  FiTrendingUp,
  FiActivity,
  FiGlobe,
  FiFileText,
  FiZap,
  FiSearch
} from 'react-icons/fi';
import { Badge } from '@/components/ui/Badge';

export default function AdminGestionComercialPage() {
  const { facturas, isLoading, isError } = useComercialApi();

  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-slate-100 pb-8">
        <div>
          <h1 className="text-4xl font-black text-slate-900 dark:text-white tracking-tighter uppercase leading-none mb-2">Omnicanalidad y Ventas Globales</h1>
          <p className="text-slate-500 dark:text-slate-400 text-lg">Monitoreo transaccional de la Triple Vía y embudos de conversión.</p>
        </div>
        <div className="flex gap-4">
           <Button className="bg-brand text-white font-black px-8 py-6 rounded-2xl shadow-xl shadow-brand/20">
              Analítica de Conversión
           </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
         <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8 group overflow-hidden relative">
            <div className="absolute right-0 top-0 p-8 opacity-5 text-brand transition-transform group-hover:scale-110 duration-700">
               <FiGlobe size={120} />
            </div>
            <p className="text-slate-400 font-bold uppercase tracking-widest text-[10px] mb-2">GMV Consolidado</p>
            <h3 className="text-4xl font-black text-slate-900 dark:text-white">$842k</h3>
            <div className="mt-4 flex items-center gap-2 text-emerald-600 font-bold text-xs">
               <FiTrendingUp /> <span>+22% vs mes anterior</span>
            </div>
         </Card>

         <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8 group overflow-hidden relative">
            <div className="absolute right-0 top-0 p-8 opacity-5 text-brand transition-transform group-hover:scale-110 duration-700">
               <FiZap size={120} />
            </div>
            <p className="text-slate-400 font-bold uppercase tracking-widest text-[10px] mb-2">Leads Activos</p>
            <h3 className="text-4xl font-black text-slate-900 dark:text-white">154</h3>
            <div className="mt-4 flex items-center gap-2 text-indigo-600 font-bold text-xs">
               <FiActivity /> <span>SADI gestionando 84% de interacciones</span>
            </div>
         </Card>

         <Card className="border-none shadow-sm bg-slate-900 text-white p-8">
            <p className="text-brand-light font-black uppercase tracking-widest text-[10px] mb-4 italic">Alerta de Optimización</p>
            <h3 className="text-2xl font-black leading-tight mb-6">El embudo de "Artesanos" requiere ajuste de oferta.</h3>
            <Button className="w-full bg-brand hover:bg-brand-light font-black py-4 rounded-xl">Aplicar Ajuste IA</Button>
         </Card>
      </div>

      <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/10 overflow-hidden">
        <CardHeader className="p-8 border-b border-slate-50 dark:border-white/5 flex flex-row items-center justify-between">
          <CardTitle className="text-xl font-bold flex items-center gap-3 italic text-brand">
             <FiFileText /> Monitor de Facturación Sistémica
          </CardTitle>
          <div className="relative">
             <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
             <input type="text" placeholder="Factura o Cliente..." className="pl-9 pr-4 py-2 bg-slate-50 dark:bg-black/20 border-none rounded-lg text-xs" />
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading && (!facturas || facturas.length === 0) ? (
            <div className="p-20 space-y-4">
               {[...Array(3)].map((_, i) => <div key={i} className="h-12 bg-slate-50 dark:bg-white/5 rounded-xl animate-pulse" />)}
            </div>
          ) : (
            <Table>
               <TableHeader className="bg-slate-50 dark:bg-black/20">
                  <TableRow>
                    <TableHead className="font-bold text-[10px] uppercase tracking-widest px-8">N° Operación</TableHead>
                    <TableHead className="font-bold text-[10px] uppercase tracking-widest">Titular / Cliente</TableHead>
                    <TableHead className="font-bold text-[10px] uppercase tracking-widest">Fecha</TableHead>
                    <TableHead className="font-bold text-[10px] uppercase tracking-widest text-right px-8">Monto Transado</TableHead>
                  </TableRow>
               </TableHeader>
               <TableBody>
                  {(facturas || []).map((factura: any) => (
                    <TableRow key={factura.id} className="hover:bg-slate-50 dark:hover:bg-white/5 transition-colors border-slate-50 dark:border-white/5">
                      <TableCell className="font-mono text-xs font-black text-brand px-8">{factura.number}</TableCell>
                      <TableCell className="font-bold text-slate-700 dark:text-slate-200">{factura.cliente_nombre}</TableCell>
                      <TableCell className="text-[10px] text-slate-400 font-black uppercase tracking-widest">{new Date(factura.issue_date).toLocaleDateString()}</TableCell>
                      <TableCell className="text-right font-black text-slate-900 dark:text-white px-8">${parseFloat(factura.total).toLocaleString()}</TableCell>
                    </TableRow>
                  ))}
                  {(!facturas || facturas.length === 0) && !isLoading && (
                    <TableRow>
                       <TableCell colSpan={4} className="text-center py-24 text-slate-400 font-bold italic uppercase tracking-widest text-xs">
                          Sin transacciones registradas en el periodo actual.
                       </TableCell>
                    </TableRow>
                  )}
               </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
