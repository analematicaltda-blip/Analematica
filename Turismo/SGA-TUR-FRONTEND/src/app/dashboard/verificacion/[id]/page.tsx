'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/Table';
import api from '@/services/api';
import { FiSave, FiXCircle, FiCheck } from 'react-icons/fi';
import { toast } from 'react-toastify';

export default function FormularioVerificacionPage() {
  const { id } = useParams();
  const router = useRouter();
  const [verificacion, setVerificacion] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [responses, setResponses] = useState<any[]>([]);

  useEffect(() => {
    api.get(`/admin/verificaciones/${id}/`).then(res => {
      setVerificacion(res.data);
      // Inicializar respuestas si la plantilla tiene items
      if (res.data.plantilla_usada?.items) {
          setResponses(res.data.plantilla_usada.items.map((item: any) => ({
              item_original_id: item.id,
              cumple: false,
              justificacion: ''
          })));
      }
      setLoading(false);
    });
  }, [id]);

  const handleToggleCumple = (itemId: number) => {
    setResponses(prev => prev.map(r =>
        r.item_original_id === itemId ? { ...r, cumple: !r.cumple } : r
    ));
  };

  const handleJustificacionChange = (itemId: number, text: string) => {
    setResponses(prev => prev.map(r =>
        r.item_original_id === itemId ? { ...r, justificacion: text } : r
    ));
  };

  const handleSave = async () => {
    try {
      await api.patch(`/admin/verificaciones/${id}/`, {
        respuestas_items: responses,
        observaciones_generales: "Visita técnica realizada por el funcionario profesional."
      });
      toast.success("Verificación guardada y puntaje actualizado.");
      router.push('/dashboard/verificacion');
    } catch (e) {
      toast.error("Error al guardar la verificación.");
    }
  };

  if (loading) return <div className="p-10 text-center animate-pulse text-slate-400 font-black uppercase tracking-widest">Iniciando Protocolo de Verificación...</div>;

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header className="flex justify-between items-end">
        <div>
           <h1 className="text-3xl font-black text-slate-900 tracking-tight uppercase italic leading-none">Formato de Verificación</h1>
           <p className="text-slate-500 font-medium mt-2">Visita técnica de cumplimiento legal y operativo.</p>
        </div>
        <div className="flex gap-4">
           <Button variant="outline" onClick={() => router.back()} className="rounded-xl font-bold uppercase text-[10px] tracking-widest px-6">Cancelar</Button>
           <Button onClick={handleSave} className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-black uppercase text-[10px] tracking-widest px-8 shadow-lg shadow-indigo-200">
              <FiSave className="mr-2" /> Certificar Visita
           </Button>
        </div>
      </header>

      <Card className="border-none shadow-2xl rounded-[3rem] overflow-hidden bg-white">
        <div className="bg-slate-900 p-10 text-white">
           <div className="grid grid-cols-2 gap-10">
              <div>
                 <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Plantilla Aplicada</p>
                 <h2 className="text-xl font-bold">{verificacion.plantilla_nombre}</h2>
              </div>
              <div>
                 <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Funcionario Evaluador</p>
                 <h2 className="text-xl font-bold">{verificacion.funcionario_nombre}</h2>
              </div>
           </div>
        </div>

        <CardContent className="p-0">
           <Table>
              <TableHeader className="bg-slate-50">
                 <TableRow>
                    <TableHead className="px-10 py-6 font-black uppercase text-[10px] tracking-widest text-slate-500">Requisito Legal / Técnico</TableHead>
                    <TableHead className="font-black uppercase text-[10px] tracking-widest text-slate-500 text-center">Cumple</TableHead>
                    <TableHead className="px-10 font-black uppercase text-[10px] tracking-widest text-slate-500">Soporte / Justificación</TableHead>
                 </TableRow>
              </TableHeader>
              <TableBody>
                 {verificacion.plantilla_usada?.items?.map((item: any) => {
                    const resp = responses.find(r => r.item_original_id === item.id);
                    return (
                       <TableRow key={item.id} className="hover:bg-slate-50/50 transition-colors">
                          <TableCell className="px-10 py-6">
                             <p className="font-bold text-slate-800">{item.texto_requisito}</p>
                             <p className="text-[9px] text-slate-400 font-black uppercase mt-1">Puntos: {item.puntaje}</p>
                          </TableCell>
                          <TableCell className="text-center">
                             <button
                                onClick={() => handleToggleCumple(item.id)}
                                className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all ${
                                   resp?.cumple
                                   ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-200'
                                   : 'bg-slate-100 text-slate-300'
                                }`}
                             >
                                <FiCheck size={24} />
                             </button>
                          </TableCell>
                          <TableCell className="px-10">
                             <input
                                type="text"
                                value={resp?.justificacion || ''}
                                onChange={(e) => handleJustificacionChange(item.id, e.target.value)}
                                placeholder="N° de Resolución, Fecha, etc."
                                className="w-full bg-slate-50 border-none px-4 py-3 rounded-xl text-sm font-medium focus:ring-2 focus:ring-indigo-500"
                             />
                          </TableCell>
                       </tr>
                    );
                 })}
              </TableBody>
           </Table>
        </CardContent>
      </Card>
    </div>
  );
}
