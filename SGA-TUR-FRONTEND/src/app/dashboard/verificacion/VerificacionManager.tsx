'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import api from '@/services/api';
import { FiCheckCircle, FiAlertCircle, FiClipboard, FiArrowRight } from 'react-icons/fi';
import { toast } from 'react-toastify';

export default function VerificacionManager() {
  const [providers, setProviders] = useState<any[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get('/v1/providers/tourism-providers/'),
      api.get('/admin/plantillas-verificacion/')
    ]).then(([provRes, tempRes]) => {
      setProviders(provRes.data.results || []);
      setTemplates(tempRes.data.results || []);
      setLoading(false);
    });
  }, []);

  const handleStartVerification = async (providerId: string) => {
    // Para simplificar, usamos la primera plantilla encontrada (Rural)
    const template = templates.find(t => t.nombre.includes('RURAL')) || templates[0];
    if (!template) {
      toast.error("No hay plantillas de verificación configuradas.");
      return;
    }

    try {
      const res = await api.post('/admin/verificaciones/iniciar/', {
        plantilla_id: template.id,
        prestador_ref_id: providerId
      });
      toast.success("Visita de verificación iniciada.");
      // Redirigir al formulario de llenado (placeholder por ahora)
      window.location.href = `/dashboard/verificacion/${res.data.id}`;
    } catch (e) {
      toast.error("Error al iniciar verificación.");
    }
  };

  if (loading) return <div className="p-10 text-center animate-pulse">Cargando prestadores...</div>;

  return (
    <div className="space-y-8 p-6">
      <header>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Control de Cumplimiento</h1>
        <p className="text-slate-500">Supervisión técnica y legal de prestadores turísticos (Vía 1).</p>
      </header>

      <Card className="border-none shadow-xl rounded-[2.5rem]">
        <CardContent className="p-0">
          <Table>
            <TableHeader className="bg-slate-50">
              <TableRow>
                <TableHead className="px-8 py-6 font-black uppercase text-[10px] tracking-widest">Establecimiento</TableHead>
                <TableHead className="font-black uppercase text-[10px] tracking-widest">Tipo</TableHead>
                <TableHead className="font-black uppercase text-[10px] tracking-widest">Puntaje Actual</TableHead>
                <TableHead className="font-black uppercase text-[10px] tracking-widest">Estado</TableHead>
                <TableHead className="text-right px-8 font-black uppercase text-[10px] tracking-widest">Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {providers.map((p) => (
                <TableRow key={p.id} className="hover:bg-slate-50/50 transition-colors">
                  <TableCell className="px-8 py-6">
                    <p className="font-bold text-slate-900">{p.name}</p>
                    <p className="text-[10px] text-slate-400 font-medium">NIT: {p.business_profile?.tax_id || 'Pendiente'}</p>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="rounded-lg font-black text-[9px] uppercase tracking-tighter">
                      {p.provider_type}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                       <span className="text-lg font-black text-indigo-600">{p.puntuacion_total || 0}</span>
                       <span className="text-[9px] text-slate-400 font-bold uppercase">pts</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1.5 text-emerald-600 font-bold text-xs uppercase tracking-tighter">
                       <FiCheckCircle /> Verificado
                    </div>
                  </TableCell>
                  <TableCell className="text-right px-8">
                    <Button
                      onClick={() => handleStartVerification(p.id)}
                      className="bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-black uppercase text-[10px] tracking-widest px-4 py-2"
                    >
                      Nueva Visita <FiArrowRight className="ml-2" />
                    </Button>
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
