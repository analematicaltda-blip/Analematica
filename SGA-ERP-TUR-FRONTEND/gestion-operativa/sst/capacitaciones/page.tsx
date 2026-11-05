'use client';
import React, { useEffect, useState } from 'react';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { FiUsers, FiBookOpen, FiAward, FiPlus, FiArrowUpRight } from 'react-icons/fi';

export default function CapacitacionesPage() {
  const { getSSTCapacitaciones, isLoading } = useMiNegocioApi();
  const [caps, setCaps] = useState<any[]>([]);

  useEffect(() => {
    getSSTCapacitaciones().then(res => res && setCaps(res));
  }, [getSSTCapacitaciones]);

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 className="text-3xl font-black uppercase italic text-slate-900 dark:text-white leading-tight">Formación y Capacitación</h1>
          <p className="text-slate-500">Gestión estratégica del conocimiento y competencias preventivas para el talento humano.</p>
        </div>
        <Button className="bg-brand hover:bg-brand-deep text-white font-black px-8 h-14 rounded-2xl shadow-xl shadow-brand/20 transition-all group">
          <FiPlus className="mr-2 group-hover:rotate-90 transition-transform" /> Programar Nueva Formación
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
         <Card className="p-8 border-none shadow-sm bg-white dark:bg-brand-deep/20 rounded-[2rem] hover:translate-y-[-4px] transition-transform">
            <div className="p-3 bg-brand/10 text-brand rounded-2xl w-fit mb-6">
               <FiUsers size={24} />
            </div>
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-1 font-mono">Cobertura Total</p>
            <h3 className="text-3xl font-black">{caps.reduce((acc, curr) => acc + curr.asistentes_count, 0)} <span className="text-xs text-slate-400 font-medium">PERSONAS</span></h3>
         </Card>

         <Card className="p-8 border-none shadow-sm bg-white dark:bg-brand-deep/20 rounded-[2rem] hover:translate-y-[-4px] transition-transform">
            <div className="p-3 bg-indigo-500/10 text-indigo-500 rounded-2xl w-fit mb-6">
               <FiBookOpen size={24} />
            </div>
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-1 font-mono">Inversión Tiempo</p>
            <h3 className="text-3xl font-black">{caps.reduce((acc, curr) => acc + (curr.intensidad_horaria || 0), 0)} <span className="text-xs text-slate-400 font-medium">HORAS</span></h3>
         </Card>

         <Card className="p-8 border-none shadow-sm bg-white dark:bg-brand-deep/20 rounded-[2rem] hover:translate-y-[-4px] transition-transform">
            <div className="p-3 bg-emerald-500/10 text-emerald-500 rounded-2xl w-fit mb-6">
               <FiAward size={24} />
            </div>
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-1 font-mono">Evaluación Promedio</p>
            <h3 className="text-3xl font-black text-emerald-600">4.8 <span className="text-xs text-slate-400 font-medium">/ 5.0</span></h3>
         </Card>

         <Card className="p-8 border-none shadow-sm bg-slate-900 text-white rounded-[2rem] flex flex-col justify-between">
            <p className="text-[10px] font-black uppercase tracking-widest text-brand-light">Estatus Normativo</p>
            <h3 className="text-xl font-bold italic leading-tight mb-4">Módulo de Certificados Digitales Activo</h3>
            <Button variant="ghost" className="p-0 text-brand-light hover:text-white justify-start font-black uppercase text-[10px] tracking-widest">
               Ver Repositorio <FiArrowUpRight className="ml-2" />
            </Button>
         </Card>
      </div>

      <Card className="border-none shadow-sm overflow-hidden bg-white dark:bg-brand-deep/10 rounded-[2.5rem]">
        <CardContent className="p-0">
          <Table>
            <TableHeader className="bg-slate-50 dark:bg-black/30">
              <TableRow>
                <TableHead className="px-10 py-6 font-black uppercase text-[10px] tracking-widest">Contenido / Tema de Formación</TableHead>
                <TableHead className="font-black uppercase text-[10px] tracking-widest">Fecha de Ejecución</TableHead>
                <TableHead className="font-black uppercase text-[10px] tracking-widest text-center">Intensidad</TableHead>
                <TableHead className="font-black uppercase text-[10px] tracking-widest text-center">Asistentes</TableHead>
                <TableHead className="font-black uppercase text-[10px] tracking-widest text-center">Estado</TableHead>
                <TableHead className="px-10 text-right font-black uppercase text-[10px] tracking-widest">Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {caps.map((c, i) => (
                <TableRow key={i} className="border-slate-50 dark:border-white/5 hover:bg-slate-50/50 dark:hover:bg-white/5 transition-colors">
                  <TableCell className="px-10 py-6">
                     <p className="font-black text-slate-800 dark:text-slate-200 text-lg tracking-tight">{c.tema}</p>
                     <p className="text-[10px] font-bold text-slate-400 uppercase">Capacitador: SADI Agent v4</p>
                  </TableCell>
                  <TableCell className="text-sm font-semibold text-slate-600 dark:text-slate-400">{new Date(c.fecha).toLocaleDateString('es-CO', { year: 'numeric', month: 'long', day: 'numeric' })}</TableCell>
                  <TableCell className="text-center">
                     <Badge variant="outline" className="font-mono bg-slate-50 dark:bg-black/40 border-slate-200">{c.intensidad_horaria}H</Badge>
                  </TableCell>
                  <TableCell className="text-center font-bold text-slate-700 dark:text-slate-300">{c.asistentes_count}</TableCell>
                  <TableCell className="text-center">
                    <Badge className={c.realizada ? 'bg-emerald-100 text-emerald-700 font-black' : 'bg-blue-100 text-blue-700 font-black'}>
                      {c.realizada ? 'CONCLUIDA' : 'PROGRAMADA'}
                    </Badge>
                  </TableCell>
                  <TableCell className="px-10 text-right">
                    <Button variant="ghost" size="sm" className="text-brand font-black uppercase text-[10px] tracking-widest hover:bg-brand/5 rounded-xl px-4">Descargar Evidencias</Button>
                  </TableCell>
                </TableRow>
              ))}
              {caps.length === 0 && !isLoading && (
                 <TableRow>
                    <TableCell colSpan={6} className="p-32 text-center text-slate-400 italic font-medium">
                       <FiBookOpen size={48} className="mx-auto mb-4 opacity-10" />
                       No se registran ciclos de formación en el historial.
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
