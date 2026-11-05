'use client';
import React, { useEffect, useState } from 'react';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { FiPlus, FiAlertCircle, FiFilter, FiDownload } from 'react-icons/fi';

export default function RiesgosPage() {
  const { getSSTRisks, isLoading } = useMiNegocioApi();
  const [risks, setRisks] = useState<any[]>([]);

  useEffect(() => {
    getSSTRisks().then(res => res && setRisks(res));
  }, [getSSTRisks]);

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black uppercase italic text-slate-900 dark:text-white">Matriz de Riesgos</h1>
          <p className="text-slate-500">Identificación, evaluación y valoración de riesgos laborales (IPERC).</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="font-bold"><FiFilter className="mr-2"/> Filtros</Button>
          <Button variant="outline" className="font-bold"><FiDownload className="mr-2"/> Exportar</Button>
          <Button className="bg-brand text-white font-black px-6 shadow-lg shadow-brand/20">
            <FiPlus className="mr-2"/> Identificar Peligro
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[
          { label: 'Total Riesgos', value: risks.length, color: 'text-slate-900' },
          { label: 'Críticos', value: risks.filter(r => r.criticidad === 'CRITICA').length, color: 'text-red-600' },
          { label: 'Altos', value: risks.filter(r => r.criticidad === 'ALTA').length, color: 'text-orange-500' },
          { label: 'Aceptables', value: risks.filter(r => r.criticidad === 'BAJA').length, color: 'text-emerald-500' },
        ].map((stat, i) => (
          <Card key={i} className="border-none shadow-sm p-6">
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-1">{stat.label}</p>
            <p className={`text-3xl font-black ${stat.color}`}>{stat.value}</p>
          </Card>
        ))}
      </div>

      <Card className="border-none shadow-sm overflow-hidden">
        <CardHeader className="bg-slate-50 dark:bg-black/20 border-b dark:border-white/5 p-6">
          <CardTitle className="text-lg font-bold flex items-center gap-2">
            <FiAlertCircle className="text-brand" /> Registro Maestro de Peligros
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader className="bg-slate-50/50 dark:bg-black/40">
              <TableRow>
                <TableHead className="uppercase text-[10px] font-bold px-8">Clasificación</TableHead>
                <TableHead className="uppercase text-[10px] font-bold">Descripción / Peligro</TableHead>
                <TableHead className="uppercase text-[10px] font-bold text-center">Prob.</TableHead>
                <TableHead className="uppercase text-[10px] font-bold text-center">Cons.</TableHead>
                <TableHead className="uppercase text-[10px] font-bold text-center">NR</TableHead>
                <TableHead className="uppercase text-[10px] font-bold text-center">Criticidad</TableHead>
                <TableHead className="uppercase text-[10px] font-bold text-right px-8">Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {risks.map((r, i) => (
                <TableRow key={i} className="hover:bg-slate-50 dark:hover:bg-white/5 transition-colors border-slate-50 dark:border-white/5">
                  <TableCell className="px-8 font-bold text-slate-700 dark:text-slate-200">{r.clasificacion}</TableCell>
                  <TableCell className="max-w-md">
                    <p className="font-semibold text-sm">{r.peligro_descripcion}</p>
                    <p className="text-xs text-slate-400 truncate">{r.efectos_posibles}</p>
                  </TableCell>
                  <TableCell className="text-center">{r.probabilidad}</TableCell>
                  <TableCell className="text-center">{r.consecuencia}</TableCell>
                  <TableCell className="text-center font-black">{r.nivel_riesgo}</TableCell>
                  <TableCell className="text-center">
                    <Badge className={
                      r.criticidad === 'CRITICA' ? 'bg-red-600 text-white' :
                      r.criticidad === 'ALTA' ? 'bg-orange-500 text-white' :
                      r.criticidad === 'MEDIA' ? 'bg-amber-400 text-black' :
                      'bg-emerald-500 text-white'
                    }>
                      {r.criticidad}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right px-8 space-x-2">
                    <Button variant="ghost" size="sm" className="text-[10px] font-bold uppercase tracking-widest text-brand">Controles</Button>
                    <Button variant="ghost" size="sm" className="text-[10px] font-bold uppercase tracking-widest">Editar</Button>
                  </TableCell>
                </TableRow>
              ))}
              {risks.length === 0 && !isLoading && (
                <TableRow>
                  <TableCell colSpan={7} className="p-20 text-center text-slate-400 italic">
                    No se han registrado peligros en la matriz.
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
