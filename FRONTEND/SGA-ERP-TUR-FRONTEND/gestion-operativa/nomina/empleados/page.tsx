'use client';
import React, { useEffect, useState } from 'react';
import { useMiNegocioApi } from '../../../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { FiPlus, FiUser, FiMail, FiPhone, FiFilter, FiDownload } from 'react-icons/fi';

export default function EmpleadosPage() {
  const { getEmpleados, isLoading } = useMiNegocioApi();
  const [employees, setEmployees] = useState<any[]>([]);

  useEffect(() => {
    getEmpleados().then(res => res && setEmployees(res));
  }, [getEmpleados]);

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black uppercase italic text-slate-900 dark:text-white tracking-tighter">Gestión de Empleados</h1>
          <p className="text-slate-500 font-medium">Control integral de hojas de vida, contratos y cargos.</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="font-bold border-slate-200"><FiFilter className="mr-2"/> Filtros</Button>
          <Button className="bg-brand text-white font-black px-6 shadow-lg shadow-brand/20">
            <FiPlus className="mr-2"/> Vincular Empleado
          </Button>
        </div>
      </div>

      <Card className="border-none shadow-sm overflow-hidden bg-white dark:bg-brand-deep/10 rounded-[2rem]">
        <CardContent className="p-0">
          <Table>
            <TableHeader className="bg-slate-50 dark:bg-black/40">
              <TableRow>
                <TableHead className="uppercase text-[10px] font-black px-10 py-6">Nombre y Cargo</TableHead>
                <TableHead className="uppercase text-[10px] font-black">Identificación</TableHead>
                <TableHead className="uppercase text-[10px] font-black">Contacto</TableHead>
                <TableHead className="uppercase text-[10px] font-black text-center">Estado</TableHead>
                <TableHead className="uppercase text-[10px] font-black text-right px-10">Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {employees.map((emp, i) => (
                <TableRow key={i} className="hover:bg-slate-50/50 dark:hover:bg-white/5 transition-colors border-slate-50 dark:border-white/5">
                  <TableCell className="px-10 py-6">
                    <div className="flex items-center gap-4">
                       <div className="w-10 h-10 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center font-black">
                          {emp.nombre[0]}{emp.apellido[0]}
                       </div>
                       <div>
                          <p className="font-black text-slate-800 dark:text-white text-lg tracking-tight">{emp.nombre} {emp.apellido}</p>
                          <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">{emp.cargo || 'CARGO NO ASIGNADO'}</p>
                       </div>
                    </div>
                  </TableCell>
                  <TableCell className="font-mono text-sm font-bold text-slate-600 dark:text-slate-400">
                    {emp.identificacion}
                  </TableCell>
                  <TableCell>
                     <div className="space-y-1">
                        <p className="text-xs flex items-center gap-2 text-slate-500 font-medium"><FiMail className="text-brand" /> {emp.email}</p>
                        <p className="text-xs flex items-center gap-2 text-slate-500 font-medium"><FiPhone className="text-brand" /> {emp.telefono}</p>
                     </div>
                  </TableCell>
                  <TableCell className="text-center">
                    <Badge className={
                      emp.estado === 'ACTIVO' ? 'bg-emerald-100 text-emerald-700 font-black' :
                      'bg-slate-100 text-slate-700 font-black'
                    }>
                      {emp.estado}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right px-10">
                    <div className="flex justify-end gap-2">
                       <Button variant="ghost" size="sm" className="text-brand font-black uppercase text-[10px] tracking-widest">Contrato</Button>
                       <Button variant="ghost" size="sm" className="text-slate-400 font-black uppercase text-[10px] tracking-widest">Editar</Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
              {employees.length === 0 && !isLoading && (
                <TableRow>
                  <TableCell colSpan={5} className="p-32 text-center text-slate-400 italic font-medium">
                    <FiUser size={48} className="mx-auto mb-4 opacity-5" />
                    No se registran empleados vinculados a la organización.
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
