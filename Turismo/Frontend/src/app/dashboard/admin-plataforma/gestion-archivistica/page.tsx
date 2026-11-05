'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import {
  FiArchive,
  FiShield,
  FiActivity,
  FiCpu,
  FiLayers,
  FiSearch,
  FiExternalLink
} from 'react-icons/fi';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';

export default function AdminGestionArchivisticaPage() {
  const archives = [
    { name: 'Cámara de Comercio - Sector Centro', status: 'VERIFIED', node: 'Node-12', date: '2024-08-20' },
    { name: 'RNT - Hotelería Regional', status: 'PENDING', node: 'Node-05', date: '2024-08-21' },
    { name: 'Contratos Laborales - Nodo Gaitan', status: 'VERIFIED', node: 'Node-08', date: '2024-08-19' },
  ];

  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-4xl font-black text-slate-900 dark:text-white tracking-tighter uppercase">Archivo Digital Soberano</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-2 text-lg">Custodia y validación descentralizada de la memoria documental del ecosistema.</p>
        </div>
        <div className="flex gap-4">
           <Button className="bg-slate-900 text-white font-black px-8 py-6 rounded-2xl">
              Audit Blockchain
           </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
         <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8 overflow-hidden relative">
            <div className="absolute right-0 top-0 p-8 opacity-5 text-indigo-600">
               <FiShield size={120} />
            </div>
            <p className="text-slate-400 font-bold uppercase tracking-widest text-xs mb-2">Integridad Global</p>
            <h3 className="text-3xl font-black text-slate-900 dark:text-white">100%</h3>
            <p className="mt-4 text-xs text-emerald-600 font-bold">Sin anomalías detectadas en red.</p>
         </Card>

         <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8 overflow-hidden relative">
            <div className="absolute right-0 top-0 p-8 opacity-5 text-indigo-600">
               <FiCpu size={120} />
            </div>
            <p className="text-slate-400 font-bold uppercase tracking-widest text-xs mb-2">Documentos Notarizados</p>
            <h3 className="text-3xl font-black text-slate-900 dark:text-white">4,285</h3>
            <p className="mt-4 text-xs text-slate-400 font-bold tracking-tighter italic">Sincronizado con Polygon Mainnet</p>
         </Card>

         <Card className="border-none shadow-sm bg-brand text-white p-8 overflow-hidden relative">
            <div className="absolute right-[-10%] bottom-[-10%] opacity-20">
               <FiLayers size={150} />
            </div>
            <p className="text-white/60 font-bold uppercase tracking-widest text-xs mb-4">Storage Used</p>
            <h3 className="text-3xl font-black italic">1.2 TB</h3>
            <p className="mt-4 text-xs font-medium text-white/80">Cifrado con grado militar AES-256.</p>
         </Card>
      </div>

      <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/10 overflow-hidden">
         <CardHeader className="p-8 border-b border-slate-50 dark:border-white/5 flex flex-row items-center justify-between">
            <CardTitle className="text-xl font-bold flex items-center gap-3 italic text-brand">
               <FiArchive /> Monitor de Trazabilidad
            </CardTitle>
            <div className="relative">
               <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
               <input type="text" placeholder="Hash o Código..." className="pl-9 pr-4 py-2 bg-slate-50 dark:bg-black/20 border-none rounded-lg text-xs" />
            </div>
         </CardHeader>
         <CardContent className="p-0">
            <Table>
               <TableHeader className="bg-slate-50 dark:bg-black/40">
                  <TableRow>
                     <TableHead className="font-bold text-[10px] uppercase tracking-widest px-8">Nombre / Soporte</TableHead>
                     <TableHead className="font-bold text-[10px] uppercase tracking-widest">Nodo de Origen</TableHead>
                     <TableHead className="font-bold text-[10px] uppercase tracking-widest">Estado Legal</TableHead>
                     <TableHead className="font-bold text-[10px] uppercase tracking-widest text-right px-8">Audit</TableHead>
                  </TableRow>
               </TableHeader>
               <TableBody>
                  {archives.map((arc, i) => (
                    <TableRow key={i} className="hover:bg-slate-50 dark:hover:bg-white/5 transition-colors border-slate-50 dark:border-white/5">
                       <TableCell className="px-8 py-6">
                          <div>
                             <p className="font-black text-slate-900 dark:text-white mb-1 uppercase tracking-tighter">{arc.name}</p>
                             <p className="text-[10px] text-slate-400 font-bold italic tracking-widest">{arc.date}</p>
                          </div>
                       </TableCell>
                       <TableCell className="font-mono text-xs font-bold text-slate-500">{arc.node}</TableCell>
                       <TableCell>
                          <Badge className={arc.status === 'VERIFIED' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}>
                             {arc.status}
                          </Badge>
                       </TableCell>
                       <TableCell className="text-right px-8">
                          <Button variant="ghost" size="sm" className="h-10 w-10 p-0 hover:bg-brand/10 hover:text-brand"><FiExternalLink size={18} /></Button>
                       </TableCell>
                    </TableRow>
                  ))}
               </TableBody>
            </Table>
         </CardContent>
      </Card>
    </div>
  );
}
