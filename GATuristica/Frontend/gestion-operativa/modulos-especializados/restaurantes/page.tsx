'use client';

import React, { useState } from 'react';
import useSWR from 'swr';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  FiGrid,
  FiPlus,
  FiLayout,
  FiSettings,
  FiActivity,
  FiShoppingBag
} from 'react-icons/fi';
import { Badge } from '@/components/ui/Badge';
import api from '@/services/api';

interface RestaurantTable {
    id: number;
    table_number: string;
    capacity: number;
    status: 'FREE' | 'OCCUPIED' | 'RESERVED' | 'DIRTY';
    pos_x: number;
    pos_y: number;
}

const fetcher = (url: string) => api.get(url).then(res => res.data.results || []);

const statusConfig = {
    FREE: { bg: 'bg-emerald-500', text: 'LIBRE' },
    OCCUPIED: { bg: 'bg-red-500', text: 'OCUPADA' },
    RESERVED: { bg: 'bg-amber-500', text: 'RESERVADA' },
    DIRTY: { bg: 'bg-slate-400', text: 'SUCIA' },
};

import { useMiNegocioApi } from '../../../hooks/useMiNegocioApi';
import { toast } from 'react-toastify';
import Modal from '@/components/ui/Modal';
import { useForm } from 'react-hook-form';

export default function RestaurantFloorPlanPage() {
    const { createRestaurantTable, deleteRestaurantTable } = useMiNegocioApi();
    const { data: tables, mutate, isLoading } = useSWR<RestaurantTable[]>('/v1/mi-negocio/operativa/restaurante/tables/', fetcher);
    const [isEditMode, setIsEditMode] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const { register, handleSubmit, reset } = useForm();

    const onSubmit = async (data: any) => {
        const res = await createRestaurantTable({
            ...data,
            pos_x: 100, // Por defecto
            pos_y: 100
        });
        if (res) {
            toast.success("Mesa registrada");
            mutate();
            setIsModalOpen(false);
            reset();
        }
    };

    return (
        <div className="space-y-10 animate-in zoom-in-95 duration-700">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div>
                    <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight uppercase italic leading-none mb-2">Control de Salón y Mesas</h1>
                    <p className="text-slate-500 dark:text-slate-400 text-lg">Visualización en tiempo real de la ocupación y gestión del servicio.</p>
                </div>
                <div className="flex gap-4">
                   <Button variant="outline" onClick={() => setIsEditMode(!isEditMode)} className="border-slate-200 dark:border-white/10 font-bold h-12">
                      <FiLayout className="mr-2" /> {isEditMode ? 'Guardar Layout' : 'Editar Plano'}
                   </Button>
                   <Button
                      onClick={() => setIsModalOpen(true)}
                      className="bg-brand text-white font-black h-12 px-8 shadow-xl shadow-brand/20"
                    >
                      <FiPlus className="mr-2" /> Nueva Mesa
                   </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
               {/* Sidebar de Estados */}
               <div className="space-y-4">
                  {Object.entries(statusConfig).map(([key, config]) => (
                    <Card key={key} className="border-none shadow-sm bg-white dark:bg-brand-deep/20">
                       <CardContent className="p-6 flex items-center justify-between">
                          <div className="flex items-center gap-4">
                             <div className={`w-3 h-3 rounded-full ${config.bg}`} />
                             <span className="text-xs font-black uppercase tracking-widest text-slate-500">{config.text}</span>
                          </div>
                          <span className="text-xl font-black text-slate-900 dark:text-white">0</span>
                       </CardContent>
                    </Card>
                  ))}

                  <Card className="border-none shadow-xl bg-slate-900 text-white p-8 mt-6 overflow-hidden relative">
                     <div className="absolute right-[-10%] bottom-[-10%] opacity-10">
                        <FiShoppingBag size={100} />
                     </div>
                     <p className="text-brand-light font-black uppercase tracking-widest text-[10px] mb-2 italic">Integración TPV</p>
                     <h3 className="text-xl font-black leading-tight italic">SADI puede tomar pedidos por voz.</h3>
                  </Card>
               </div>

               {/* Área del Plano */}
               <div className="lg:col-span-3">
                  <div className="bg-white dark:bg-brand-deep/10 border-2 border-dashed border-slate-200 dark:border-white/5 rounded-[3rem] h-[70vh] relative overflow-hidden shadow-inner p-10">
                     {tables?.length === 0 && !isLoading && (
                        <div className="h-full flex flex-col items-center justify-center text-center opacity-20">
                           <FiGrid size={64} />
                           <p className="mt-4 font-black text-xl">El salón está vacío.</p>
                           <p className="text-sm">Empieza a ubicar mesas en el espacio.</p>
                        </div>
                     )}

                     {tables?.map(table => (
                        <div
                            key={table.id}
                            className={`absolute w-32 h-32 rounded-3xl shadow-2xl flex flex-col justify-center items-center text-white p-4 transition-all hover:scale-105 active:scale-95 group/table
                                       ${statusConfig[table.status].bg} ${isEditMode ? 'cursor-move ring-4 ring-white/50' : 'cursor-pointer'}`}
                            style={{ left: `${table.pos_x}px`, top: `${table.pos_y}px` }}
                        >
                            <button
                                onClick={async (e) => {
                                    e.stopPropagation();
                                    if(window.confirm("¿Eliminar mesa?")) {
                                        await deleteRestaurantTable(table.id);
                                        mutate();
                                    }
                                }}
                                className="absolute -top-2 -right-2 bg-red-600 text-white rounded-full p-1 opacity-0 group-hover/table:opacity-100 transition-opacity"
                            >
                                <FiPlus className="rotate-45" size={12} />
                            </button>
                            <span className="text-[10px] font-black uppercase tracking-widest opacity-60 mb-1">Mesa</span>
                            <span className="text-3xl font-black tracking-tighter">{table.table_number}</span>
                            <Badge variant="outline" className="mt-2 bg-white/20 border-none text-[8px] font-black">{table.capacity} PAX</Badge>
                        </div>
                     ))}

                     {isLoading && (
                        <div className="h-full flex items-center justify-center">
                           <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand" />
                        </div>
                     )}
                  </div>
               </div>
            </div>

            <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Registrar Nueva Mesa">
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                    <div>
                        <label className="text-xs font-black uppercase tracking-widest text-slate-400">Identificador / Número</label>
                        <input {...register('table_number', { required: true })} className="w-full p-4 border rounded-2xl dark:bg-brand-deep mt-2" placeholder="Ej: M-01" />
                    </div>
                    <div>
                        <label className="text-xs font-black uppercase tracking-widest text-slate-400">Capacidad (PAX)</label>
                        <input type="number" {...register('capacity', { required: true })} className="w-full p-4 border rounded-2xl dark:bg-brand-deep mt-2" placeholder="4" />
                    </div>
                    <Button type="submit" className="w-full bg-brand text-white font-black py-5 rounded-2xl shadow-xl">Confirmar Registro</Button>
                </form>
            </Modal>
        </div>
    );
}
