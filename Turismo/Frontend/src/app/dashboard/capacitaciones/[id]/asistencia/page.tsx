'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import api from '@/services/api';
import { FiUsers, FiCheck, FiSearch, FiArrowLeft } from 'react-icons/fi';
import { toast } from 'react-toastify';
import Link from 'next/link';

export default function RegistroAsistenciaPage() {
  const { id } = useParams();
  const [capacitacion, setCapacitacion] = useState<any>(null);
  const [providers, setProviders] = useState<any[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get(`/v1/public/publicaciones/${id}/`), // Detalle publico o admin
      api.get('/admin/users/?role=PRESTADOR') // Solo prestadores/artesanos asisten
    ]).then(([capRes, provRes]) => {
      setCapacitacion(capRes.data);
      setProviders(provRes.data.results || []);
      setLoading(false);
    });
  }, [id]);

  const toggleSelect = (userId: number) => {
    setSelectedIds(prev =>
      prev.includes(userId) ? prev.filter(id => id !== userId) : [...prev, userId]
    );
  };

  const handleSaveAsistencia = async () => {
    try {
      await api.post(`/admin/publicaciones/${id}/registrar_asistencia/`, {
        asistentes_ids: selectedIds
      });
      toast.success("Asistencia registrada. Puntos asignados a los perfiles.");
    } catch (e) {
      toast.error("Error al registrar asistencia.");
    }
  };

  const filtered = providers.filter(p =>
    p.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (p.nombre_display && p.nombre_display.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (loading) return <div className="p-10 text-center animate-pulse font-black uppercase">Sincronizando con el nodo de formación...</div>;

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">
      <Link href="/dashboard/capacitaciones" className="text-indigo-600 font-bold flex items-center gap-2 mb-4 hover:gap-3 transition-all">
         <FiArrowLeft /> Volver a Gestión
      </Link>

      <header>
         <h1 className="text-3xl font-black text-slate-900 tracking-tight uppercase italic">{capacitacion?.titulo}</h1>
         <p className="text-slate-500 font-medium">Registro manual de asistencia (Simulación QR/Listado).</p>
      </header>

      <Card className="border-none shadow-xl rounded-[2.5rem] overflow-hidden bg-white">
        <div className="p-8 border-b border-slate-50 flex items-center gap-4 bg-slate-950">
           <div className="flex-1 relative">
              <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Buscar por nombre de negocio o usuario..."
                className="w-full bg-white/5 border-none pl-12 pr-4 py-3 rounded-xl text-white text-sm focus:ring-2 focus:ring-indigo-500"
              />
           </div>
           <Badge className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-black">{selectedIds.length} Seleccionados</Badge>
        </div>

        <CardContent className="p-0 max-h-[500px] overflow-y-auto custom-scrollbar">
           <div className="divide-y divide-slate-50">
              {filtered.map(p => (
                <div
                   key={p.id}
                   onClick={() => toggleSelect(p.id)}
                   className={`p-6 flex items-center justify-between cursor-pointer transition-colors ${
                      selectedIds.includes(p.id) ? 'bg-indigo-50' : 'hover:bg-slate-50/50'
                   }`}
                >
                   <div>
                      <p className="font-bold text-slate-800">{p.nombre_display || p.username}</p>
                      <p className="text-[10px] font-black text-slate-400 uppercase tracking-tighter">{p.rol_display}</p>
                   </div>
                   <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center transition-all ${
                      selectedIds.includes(p.id) ? 'bg-indigo-600 border-indigo-600 text-white' : 'border-slate-200 text-transparent'
                   }`}>
                      <FiCheck />
                   </div>
                </div>
              ))}
           </div>
        </CardContent>

        <div className="p-8 bg-slate-50 border-t border-slate-100 flex justify-end">
           <Button
             onClick={handleSaveAsistencia}
             disabled={selectedIds.length === 0}
             className="bg-indigo-600 text-white font-black uppercase text-[10px] tracking-widest px-10 py-5 rounded-2xl shadow-lg shadow-indigo-200"
           >
              Validar y Otorgar Puntos
           </Button>
        </div>
      </Card>
    </div>
  );
}
