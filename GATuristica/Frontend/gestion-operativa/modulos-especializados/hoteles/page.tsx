'use client';

import React, { useState } from 'react';
import useSWR from 'swr';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  FiBriefcase,
  FiPlus,
  FiHome,
  FiStar,
  FiUsers,
  FiActivity,
  FiSettings,
  FiGrid
} from 'react-icons/fi';
import { Badge } from '@/components/ui/Badge';
import api from '@/services/api';

interface Product { id: number; nombre: string; base_price: string; }
interface Amenity { id: number; nombre: string; }
interface RoomType { id: number; product: Product; capacidad: number; amenities: Amenity[]; }
interface Room { id: number; room_type: number; numero_habitacion: string; status: string; housekeeping_status: string; room_type_name: string; }

const fetcher = (url: string) => api.get(url).then(res => res.data.results || []);

import { useMiNegocioApi } from '../../../hooks/useMiNegocioApi';
import { toast } from 'react-toastify';
import Modal from '@/components/ui/Modal';
import { useForm } from 'react-hook-form';

export default function HotelManagementPage() {
    const {
        triggerMission,
        getHotelRoomTypes,
        createHotelRoomType,
        deleteHotelRoomType,
        getHotelRooms,
        createHotelRoom,
        deleteHotelRoom,
        getProductos,
        isLoading: isApiLoading
    } = useMiNegocioApi();

    const { data: roomTypes, mutate: mutateRoomTypes, isLoading: isLoadingTypes } = useSWR<RoomType[]>('/v1/mi-negocio/operativa/hotel/room-types/', fetcher);
    const { data: rooms, mutate: mutateRooms, isLoading: isLoadingRooms } = useSWR<Room[]>('/v1/mi-negocio/operativa/hotel/rooms/', fetcher);
    const [isTypeModalOpen, setIsTypeModalOpen] = useState(false);
    const [isRoomModalOpen, setIsRoomModalOpen] = useState(false);
    const [allProducts, setAllProducts] = useState<any[]>([]);

    const { register: regType, handleSubmit: handleTypeSubmit, reset: resetType } = useForm();
    const { register: regRoom, handleSubmit: handleRoomSubmit, reset: resetRoom } = useForm();

    const onTypeSubmit = async (data: any) => {
        const res = await createHotelRoomType(data);
        if (res) {
            toast.success("Tipo de habitación creado");
            mutateRoomTypes();
            setIsTypeModalOpen(false);
            resetType();
        }
    };

    const onRoomSubmit = async (data: any) => {
        const res = await createHotelRoom(data);
        if (res) {
            toast.success("Habitación creada");
            mutateRooms();
            setIsRoomModalOpen(false);
            resetRoom();
        }
    };

    useEffect(() => {
        if (isTypeModalOpen) {
            getProductos().then(res => res && setAllProducts(res.results));
        }
    }, [isTypeModalOpen, getProductos]);

    return (
        <div className="space-y-10 animate-in fade-in duration-700">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div>
                    <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight uppercase italic">Operación Hotelera</h1>
                    <p className="text-slate-500 dark:text-slate-400 mt-1 text-lg">Control de inventario de habitaciones, amenidades y servicios de alojamiento.</p>
                </div>
                <div className="flex gap-4">
                    <Button
                        onClick={() => setIsRoomModalOpen(true)}
                        variant="outline"
                        className="font-black px-8 py-6 rounded-2xl shadow-sm transition-all"
                    >
                        <FiPlus className="mr-2" /> Nueva Habitación
                    </Button>
                    <Button
                        onClick={() => setIsTypeModalOpen(true)}
                        className="bg-brand text-white font-black px-8 py-6 rounded-2xl shadow-xl shadow-brand/20 transition-all"
                    >
                        <FiPlus className="mr-2" /> Definir Tipo
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
               <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8">
                  <div className="flex justify-between items-start mb-6">
                     <div className="p-4 bg-indigo-50 text-indigo-600 rounded-2xl">
                        <FiHome size={28} />
                     </div>
                  </div>
                  <p className="text-slate-400 font-bold uppercase tracking-widest text-[10px] mb-2">Unidades Totales</p>
                  <h3 className="text-4xl font-black text-slate-900 dark:text-white">12</h3>
               </Card>

               <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8">
                  <div className="flex justify-between items-start mb-6">
                     <div className="p-4 bg-emerald-50 text-emerald-600 rounded-2xl">
                        <FiUsers size={28} />
                     </div>
                  </div>
                  <p className="text-slate-400 font-bold uppercase tracking-widest text-[10px] mb-2">Capacidad Máxima</p>
                  <h3 className="text-4xl font-black text-slate-900 dark:text-white">42</h3>
               </Card>

               <Card className="border-none shadow-xl bg-slate-900 text-white p-8 overflow-hidden relative group">
                  <div className="absolute right-0 bottom-0 p-8 opacity-10 group-hover:scale-110 transition-transform duration-700">
                     <FiActivity size={120} />
                  </div>
                  <p className="text-brand-light font-black uppercase tracking-widest text-[10px] mb-4">Estatus IA</p>
                  <h3 className="text-2xl font-black leading-tight italic">Optimización de precios por temporada activa.</h3>
               </Card>
            </div>

            <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/10 overflow-hidden rounded-[2rem]">
                <CardHeader className="p-8 border-b border-slate-50 dark:border-white/5 flex flex-row items-center justify-between bg-white dark:bg-black/40">
                   <CardTitle className="text-xl font-bold flex items-center gap-3 italic text-brand">
                      <FiGrid /> Tipos de Inventario
                   </CardTitle>
                   <Button variant="ghost" className="text-brand font-black text-xs uppercase tracking-widest">Ver Mapa de Habitaciones</Button>
                </CardHeader>
                <CardContent className="p-0">
                    <div className="divide-y divide-slate-50 dark:divide-white/5">
                        {roomTypes?.map(rt => (
                            <div key={rt.id} className="p-8 hover:bg-slate-50 dark:hover:bg-white/5 transition-all">
                                <div className="flex flex-col md:flex-row md:items-center justify-between gap-8">
                                    <div className="flex items-center gap-6">
                                       <div className="w-16 h-16 bg-slate-100 dark:bg-black/20 rounded-2xl flex items-center justify-center text-slate-400">
                                          <FiHome size={24} />
                                       </div>
                                       <div>
                                          <h3 className="text-xl font-black text-slate-900 dark:text-white uppercase tracking-tighter italic">{rt.product.nombre}</h3>
                                          <p className="text-sm text-slate-500 font-medium">Capacidad: {rt.capacidad} personas | Precio Base: ${rt.product.base_price}</p>
                                       </div>
                                    </div>
                                    <div className="flex gap-2">
                                       <Button
                                          variant="ghost"
                                          className="text-red-500 font-bold"
                                          onClick={async () => {
                                            if(window.confirm("¿Eliminar este tipo de habitación?")) {
                                                await deleteHotelRoomType(rt.id);
                                                mutateRoomTypes();
                                            }
                                          }}
                                        >
                                            Eliminar
                                        </Button>
                                       <Button
                                          className="bg-brand text-white font-black h-12 px-8"
                                          onClick={() => triggerMission('AUDIT_QUALITY', {
                                              room_type_id: rt.id,
                                              context: 'Hotel Management Audit'
                                          })}
                                          disabled={isApiLoading}
                                       >
                                          Audit
                                       </Button>
                                    </div>
                                </div>
                            </div>
                        ))}
                        {roomTypes?.length === 0 && !isLoadingTypes && (
                            <div className="p-32 text-center">
                                <FiHome size={64} className="mx-auto text-slate-200 mb-6" />
                                <h3 className="text-xl font-black text-slate-400 uppercase tracking-widest">Sin Configuración de Inventario</h3>
                                <p className="text-slate-500 mt-2">Define los tipos de habitación para habilitar la venta en la Triple Vía.</p>
                            </div>
                        )}
                        {isLoadingTypes && (
                           <div className="p-20 space-y-6">
                              {[...Array(2)].map((_, i) => <div key={i} className="h-20 bg-slate-50 dark:bg-white/5 rounded-2xl animate-pulse" />)}
                           </div>
                        )}
                    </div>
                </CardContent>
            </Card>

            <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/10 overflow-hidden rounded-[2rem]">
                <CardHeader className="p-8 border-b border-slate-50 dark:border-white/5 bg-white dark:bg-black/40">
                   <CardTitle className="text-xl font-bold flex items-center gap-3 italic text-indigo-600">
                      <FiHome /> Habitaciones Individuales
                   </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead className="px-8">N° Habitación</TableHead>
                                <TableHead>Tipo</TableHead>
                                <TableHead>Estado</TableHead>
                                <TableHead>Limpieza</TableHead>
                                <TableHead className="text-right px-8">Acciones</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {rooms?.map(room => (
                                <TableRow key={room.id}>
                                    <TableCell className="px-8 font-black">{room.numero_habitacion}</TableCell>
                                    <TableCell>{room.room_type_name}</TableCell>
                                    <TableCell>
                                        <Badge className={room.status === 'AVAILABLE' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}>
                                            {room.status}
                                        </Badge>
                                    </TableCell>
                                    <TableCell>
                                        <Badge variant="outline">{room.housekeeping_status}</Badge>
                                    </TableCell>
                                    <TableCell className="text-right px-8">
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className="text-red-500"
                                            onClick={async () => {
                                                if(window.confirm("¿Eliminar habitación?")) {
                                                    await deleteHotelRoom(room.id);
                                                    mutateRooms();
                                                }
                                            }}
                                        >
                                            Eliminar
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            {/* MODALES CRUD */}
            <Modal isOpen={isTypeModalOpen} onClose={() => setIsTypeModalOpen(false)} title="Definir Tipo de Habitación">
                <form onSubmit={handleTypeSubmit(onTypeSubmit)} className="space-y-4">
                    <div>
                        <label className="text-xs font-black uppercase">Producto Vinculado</label>
                        <select {...regType('product', { required: true })} className="w-full p-3 border rounded-xl dark:bg-brand-deep">
                            <option value="">Seleccione un producto...</option>
                            {allProducts.map(p => <option key={p.id} value={p.id}>{p.nombre} (${p.precio_venta})</option>)}
                        </select>
                    </div>
                    <div>
                        <label className="text-xs font-black uppercase">Capacidad (Personas)</label>
                        <input type="number" {...regType('capacidad', { required: true })} className="w-full p-3 border rounded-xl dark:bg-brand-deep" />
                    </div>
                    <Button type="submit" className="w-full bg-brand text-white font-black py-4">Guardar Configuración</Button>
                </form>
            </Modal>

            <Modal isOpen={isRoomModalOpen} onClose={() => setIsRoomModalOpen(false)} title="Nueva Habitación Física">
                <form onSubmit={handleRoomSubmit(onRoomSubmit)} className="space-y-4">
                    <div>
                        <label className="text-xs font-black uppercase">Número de Habitación</label>
                        <input {...regRoom('numero_habitacion', { required: true })} className="w-full p-3 border rounded-xl dark:bg-brand-deep" placeholder="Ej: 101, 204-A" />
                    </div>
                    <div>
                        <label className="text-xs font-black uppercase">Tipo de Habitación</label>
                        <select {...regRoom('room_type', { required: true })} className="w-full p-3 border rounded-xl dark:bg-brand-deep">
                            <option value="">Seleccione tipo...</option>
                            {roomTypes?.map(rt => <option key={rt.id} value={rt.id}>{rt.product.nombre}</option>)}
                        </select>
                    </div>
                    <Button type="submit" className="w-full bg-indigo-600 text-white font-black py-4">Registrar Habitación</Button>
                </form>
            </Modal>
        </div>
    );
}
