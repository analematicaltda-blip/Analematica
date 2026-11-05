'use client';

import React, { useState } from 'react';
import useSWR from 'swr';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  FiBriefcase,
  FiPlus,
  FiPackage,
  FiTrendingUp,
  FiUsers,
  FiLayers
} from 'react-icons/fi';
import { Badge } from '@/components/ui/Badge';
import api from '@/services/api';
import { useMiNegocioApi } from '../../../hooks/useMiNegocioApi';
import { toast } from 'react-toastify';
import Modal from '@/components/ui/Modal';
import { useForm } from 'react-hook-form';

interface TravelPackage {
    id: number;
    nombre: string;
    descripcion: string;
    precio_total: string;
    estado: string;
    duracion_dias: number;
}

const fetcher = (url: string) => api.get(url).then(res => res.data.results || []);

export default function AgencyManagementPage() {
    const { createTravelPackage, deleteTravelPackage } = useMiNegocioApi();
    const { data: packages, mutate, isLoading } = useSWR<TravelPackage[]>('/v1/mi-negocio/operativa/agencias/packages/', fetcher);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const { register, handleSubmit, reset } = useForm();

    const onSubmit = async (data: any) => {
        const res = await createTravelPackage(data);
        if (res) {
            toast.success("Paquete turístico creado");
            mutate();
            setIsModalOpen(false);
            reset();
        }
    };

    return (
        <div className="space-y-10 animate-in fade-in duration-700">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div>
                    <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight uppercase italic leading-none mb-2">Consolidación de Paquetes</h1>
                    <p className="text-slate-500 dark:text-slate-400 text-lg">Crea experiencias únicas integrando múltiples servicios turísticos.</p>
                </div>
                <Button
                    onClick={() => setIsModalOpen(true)}
                    className="bg-brand text-white font-black h-12 px-8 shadow-xl shadow-brand/20"
                >
                    <FiPlus className="mr-2" /> Nuevo Paquete
                </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
               <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8">
                  <FiPackage className="text-brand mb-4" size={32} />
                  <p className="text-slate-400 font-bold uppercase text-[10px] tracking-widest">Paquetes Activos</p>
                  <h3 className="text-3xl font-black">{packages?.filter(p => p.estado === 'PUBLICADO').length || 0}</h3>
               </Card>
               <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8">
                  <FiUsers className="text-indigo-600 mb-4" size={32} />
                  <p className="text-slate-400 font-bold uppercase text-[10px] tracking-widest">Reservas Confirmadas</p>
                  <h3 className="text-3xl font-black">0</h3>
               </Card>
               <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8">
                  <FiTrendingUp className="text-emerald-600 mb-4" size={32} />
                  <p className="text-slate-400 font-bold uppercase text-[10px] tracking-widest">Ventas del Mes</p>
                  <h3 className="text-3xl font-black">$0.00</h3>
               </Card>
            </div>

            <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/10 overflow-hidden rounded-[2rem]">
                <CardHeader className="p-8 border-b border-slate-50 dark:border-white/5 bg-white dark:bg-black/40">
                   <CardTitle className="text-xl font-bold flex items-center gap-3 italic text-brand">
                      <FiLayers /> Catálogo de Experiencias
                   </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                    <div className="divide-y divide-slate-50 dark:divide-white/5">
                        {packages?.map(p => (
                            <div key={p.id} className="p-8 hover:bg-slate-50 dark:hover:bg-white/5 transition-all">
                                <div className="flex flex-col md:flex-row md:items-center justify-between gap-8">
                                    <div className="flex items-center gap-6">
                                       <div className="w-16 h-16 bg-slate-100 dark:bg-black/20 rounded-2xl flex items-center justify-center text-slate-400">
                                          <FiBriefcase size={24} />
                                       </div>
                                       <div>
                                          <h3 className="text-xl font-black text-slate-900 dark:text-white uppercase tracking-tighter italic">{p.nombre}</h3>
                                          <p className="text-sm text-slate-500 font-medium">{p.duracion_dias} días | Precio: ${parseFloat(p.precio_total).toLocaleString()}</p>
                                       </div>
                                    </div>
                                    <div className="flex gap-2">
                                       <Badge className={p.estado === 'PUBLICADO' ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-700'}>
                                          {p.estado}
                                       </Badge>
                                       <Button
                                          variant="ghost"
                                          className="text-red-500 font-bold"
                                          onClick={async () => {
                                            if(window.confirm("¿Eliminar paquete?")) {
                                                await deleteTravelPackage(p.id);
                                                mutate();
                                            }
                                          }}
                                        >
                                            Eliminar
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        ))}
                        {packages?.length === 0 && !isLoading && (
                            <div className="p-32 text-center">
                                <FiPackage size={64} className="mx-auto text-slate-200 mb-6" />
                                <h3 className="text-xl font-black text-slate-400 uppercase tracking-widest">Sin Paquetes Registrados</h3>
                                <p className="text-slate-500 mt-2">Crea tu primer paquete combinando alojamiento, transporte y guías.</p>
                            </div>
                        )}
                        {isLoading && (
                           <div className="p-20 space-y-6">
                              {[...Array(2)].map((_, i) => <div key={i} className="h-20 bg-slate-50 dark:bg-white/5 rounded-2xl animate-pulse" />)}
                           </div>
                        )}
                    </div>
                </CardContent>
            </Card>

            <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Crear Nuevo Paquete Turístico">
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                    <div>
                        <label className="text-xs font-black uppercase tracking-widest text-slate-400">Nombre de la Experiencia</label>
                        <input {...register('nombre', { required: true })} className="w-full p-4 border rounded-2xl dark:bg-brand-deep mt-2" placeholder="Ej: Aventura en el Meta" />
                    </div>
                    <div>
                        <label className="text-xs font-black uppercase tracking-widest text-slate-400">Descripción Corta</label>
                        <textarea {...register('descripcion', { required: true })} className="w-full p-4 border rounded-2xl dark:bg-brand-deep mt-2" rows={3} />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="text-xs font-black uppercase tracking-widest text-slate-400">Duración (Días)</label>
                            <input type="number" {...register('duracion_dias', { required: true })} className="w-full p-4 border rounded-2xl dark:bg-brand-deep mt-2" defaultValue={1} />
                        </div>
                        <div>
                            <label className="text-xs font-black uppercase tracking-widest text-slate-400">Margen Agencia (%)</label>
                            <input type="number" {...register('margen_agencia', { required: true })} className="w-full p-4 border rounded-2xl dark:bg-brand-deep mt-2" defaultValue={10} />
                        </div>
                    </div>
                    <Button type="submit" className="w-full bg-brand text-white font-black py-5 rounded-2xl shadow-xl">Guardar Paquete</Button>
                </form>
            </Modal>
        </div>
    );
}
