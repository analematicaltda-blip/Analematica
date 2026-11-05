'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import api from '@/services/api';
import { FiUsers, FiCalendar, FiPlus, FiCheckCircle, FiAward, FiEye } from 'react-icons/fi';
import { toast } from 'react-toastify';
import Link from 'next/link';

export default function CapacitacionesManager() {
  const [capacitaciones, setCapacitaciones] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCapacitaciones();
  }, []);

  const fetchCapacitaciones = async () => {
    try {
      const res = await api.get('/admin/publicaciones/?tipo=CAPACITACION');
      setCapacitaciones(res.data.results || []);
    } catch (e) {
      toast.error("Error al cargar capacitaciones.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 p-6">
      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Ciclos de Capacitación</h1>
          <p className="text-slate-500">Gestión de formación para el fortalecimiento del ecosistema turístico.</p>
        </div>
        <Button className="bg-indigo-600 hover:bg-indigo-700 text-white font-black px-8 py-6 rounded-2xl shadow-xl shadow-indigo-200">
           <FiPlus className="mr-2" /> Nueva Capacitación
        </Button>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
         <KpiMini title="Capacitaciones" value={capacitaciones.length} icon={<FiCalendar/>} />
         <KpiMini title="Asistentes Totales" value="124" icon={<FiUsers/>} />
         <KpiMini title="Puntos Otorgados" value="1,240" icon={<FiAward/>} />
      </div>

      <Card className="border-none shadow-xl rounded-[2.5rem] overflow-hidden">
        <CardContent className="p-0">
          <Table>
            <TableHeader className="bg-slate-50">
              <TableRow>
                <TableHead className="px-8 py-6 font-black uppercase text-[10px] tracking-widest">Tema</TableHead>
                <TableHead className="font-black uppercase text-[10px] tracking-widest">Fecha</TableHead>
                <TableHead className="font-black uppercase text-[10px] tracking-widest">Puntos</TableHead>
                <TableHead className="font-black uppercase text-[10px] tracking-widest">Estado</TableHead>
                <TableHead className="text-right px-8 font-black uppercase text-[10px] tracking-widest">Control</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {capacitaciones.map((c) => (
                <TableRow key={c.id} className="hover:bg-slate-50/50 transition-colors">
                  <TableCell className="px-8 py-6 font-bold text-slate-900">{c.titulo}</TableCell>
                  <TableCell className="text-sm text-slate-500">{new Date(c.fecha_evento_inicio).toLocaleDateString()}</TableCell>
                  <TableCell>
                     <Badge className="bg-indigo-50 text-indigo-700 font-black">{c.puntos_asistencia || 10} pts</Badge>
                  </TableCell>
                  <TableCell>
                     <Badge className={c.estado === 'PUBLICADO' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}>
                        {c.estado}
                     </Badge>
                  </TableCell>
                  <TableCell className="text-right px-8">
                     <Link href={`/dashboard/capacitaciones/${c.id}/asistencia`}>
                        <Button className="bg-slate-900 text-white font-black text-[10px] tracking-widest uppercase rounded-xl">
                           <FiUsers className="mr-2" /> Registrar Asistencia (QR)
                        </Button>
                     </Link>
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

function KpiMini({ title, value, icon }: any) {
    return (
        <Card className="p-6 border-none shadow-sm bg-white rounded-3xl">
           <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-slate-50 rounded-2xl flex items-center justify-center text-slate-400">
                 {icon}
              </div>
              <div>
                 <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{title}</p>
                 <h3 className="text-2xl font-black text-slate-800">{value}</h3>
              </div>
           </div>
        </Card>
    )
}
