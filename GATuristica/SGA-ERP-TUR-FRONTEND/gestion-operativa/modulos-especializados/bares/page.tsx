'use client';

import React, { useEffect, useState } from 'react';
import api from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { FiZap, FiPlus, FiActivity, FiDollarSign, FiBox } from 'react-icons/fi';
import { Badge } from '@/components/ui/Badge';

export default function BaresManagementPage() {
  const [events, setEvents] = useState<any[]>([]);
  const [inventory, setInventory] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [evs, inv] = await Promise.all([
          api.get('/v1/mi-negocio/operativa/bares-discotecas/eventos/'),
          api.get('/v1/mi-negocio/operativa/bares-discotecas/inventario-licores/')
        ]);
        setEvents(evs.data.results || []);
        setInventory(inv.data.results || []);
      } catch (error) {
        console.error("Error loading Bares data:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-3xl font-black text-slate-900 dark:text-white uppercase italic tracking-tight">Gestión Nocturna</h1>
          <p className="text-slate-500">Control de eventos, consumo en mesa y stock de licores.</p>
        </div>
        <Button className="bg-brand text-white font-black px-8 py-6 rounded-2xl">
          <FiPlus className="mr-2" /> Programar Evento
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
         <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8">
            <FiActivity className="text-brand mb-4" size={32} />
            <p className="text-slate-400 font-bold uppercase text-[10px] tracking-widest">Eventos Activos</p>
            <h3 className="text-3xl font-black">{events.filter(e => e.estado === 'ACTIVO').length}</h3>
         </Card>
         <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8">
            <FiBox className="text-indigo-600 mb-4" size={32} />
            <p className="text-slate-400 font-bold uppercase text-[10px] tracking-widest">Referencias en Stock</p>
            <h3 className="text-3xl font-black">{inventory.length}</h3>
         </Card>
         <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8">
            <FiDollarSign className="text-emerald-600 mb-4" size={32} />
            <p className="text-slate-400 font-bold uppercase text-[10px] tracking-widest">Ventas del Turno</p>
            <h3 className="text-3xl font-black">$0.00</h3>
         </Card>
      </div>

      <Card className="border-none shadow-sm overflow-hidden">
        <CardHeader className="bg-slate-50 dark:bg-black/20 p-6 border-b dark:border-white/5">
          <CardTitle className="text-lg font-bold flex items-center gap-2">
            <FiZap className="text-brand" /> Eventos Próximos y Activos
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="px-8">Evento</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Fecha</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead className="text-right px-8">Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {events.map((e) => (
                <TableRow key={e.id}>
                  <TableCell className="px-8 font-bold">{e.nombre}</TableCell>
                  <TableCell><Badge variant="outline">{e.tipo}</Badge></TableCell>
                  <TableCell>{new Date(e.fecha_inicio).toLocaleString()}</TableCell>
                  <TableCell>
                    <Badge className={e.estado === 'ACTIVO' ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-700'}>
                      {e.estado}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right px-8">
                    <Button variant="ghost" size="sm" className="text-brand font-bold">Ver Detalles</Button>
                  </TableCell>
                </TableRow>
              ))}
              {events.length === 0 && !isLoading && (
                <TableRow>
                  <TableCell colSpan={5} className="p-20 text-center text-slate-400 italic">No hay eventos registrados.</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
