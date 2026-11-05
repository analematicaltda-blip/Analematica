'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { toast } from 'react-toastify';
import { FiEdit, FiTrash2, FiPlus, FiShield, FiTrendingUp } from 'react-icons/fi';
import api from '@/services/api';
import PlanFormModal from './PlanFormModal';
import { Badge } from '@/components/ui/Badge';

interface Plan {
    id: number;
    nombre: string;
    descripcion: string;
    precio: string;
    frecuencia: string;
    tipo_usuario_objetivo: string;
    is_active: boolean;
}

export default function PlanesPage() {
    const [planes, setPlanes] = useState<Plan[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [planToEdit, setPlanToEdit] = useState<Plan | null>(null);

    const fetchPlanes = useCallback(async () => {
        try {
            setIsLoading(true);
            const response = await api.get('/admin/plataforma/planes/');
            setPlanes(response.data.results || []);
        } catch (err) {
            // setError('No se pudieron cargar los planes.');
            toast.error('No se pudieron cargar los planes.');
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchPlanes();
    }, [fetchPlanes]);

    const handleOpenModal = (plan: Plan | null = null) => {
        setPlanToEdit(plan);
        setIsModalOpen(true);
    };

    const handleCloseModal = () => {
        setIsModalOpen(false);
        setPlanToEdit(null);
    };

    const handleSavePlan = (savedPlan: Plan) => {
        if (planToEdit) {
            setPlanes(planes.map(p => p.id === savedPlan.id ? savedPlan : p));
        } else {
            setPlanes([...planes, savedPlan]);
        }
    };

    const handleDeletePlan = async (planId: number) => {
        if (!window.confirm('¿Estás seguro de que quieres eliminar este plan?')) {
            return;
        }
        try {
            await api.delete(`/admin/plataforma/planes/${planId}/`);
            setPlanes(planes.filter(p => p.id !== planId));
            toast.success('Plan eliminado con éxito.');
        } catch (error) {
            toast.error('Error al eliminar el plan.');
        }
    };

    return (
        <div className="space-y-10 animate-in fade-in duration-700">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div>
                    <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight uppercase italic">Monetización del Ecosistema</h1>
                    <p className="text-slate-500 dark:text-slate-400 mt-1">Gestión estratégica de planes de suscripción y niveles de servicio.</p>
                </div>
                <Button onClick={() => handleOpenModal()} className="bg-brand text-white font-black px-8 py-6 rounded-2xl shadow-lg shadow-brand/20">
                    <FiPlus className="mr-2" /> Crear Nuevo Plan
                </Button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
               <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8">
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Planes Activos</p>
                  <h3 className="text-3xl font-black text-slate-900 dark:text-white">{planes.length}</h3>
               </Card>
               <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8 border-l-4 border-l-emerald-500">
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Ingresos MRR</p>
                  <h3 className="text-3xl font-black text-emerald-600">$0.00</h3>
               </Card>
            </div>

            <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/10 overflow-hidden">
                <CardContent className="p-0">
                    <Table>
                        <TableHeader className="bg-slate-50 dark:bg-black/40">
                            <TableRow>
                                <TableHead className="font-bold text-[10px] uppercase tracking-widest px-8">Nombre del Plan</TableHead>
                                <TableHead className="font-bold text-[10px] uppercase tracking-widest">Público Objetivo</TableHead>
                                <TableHead className="font-bold text-[10px] uppercase tracking-widest">Frecuencia</TableHead>
                                <TableHead className="font-bold text-[10px] uppercase tracking-widest">Precio Base</TableHead>
                                <TableHead className="font-bold text-[10px] uppercase tracking-widest">Estado</TableHead>
                                <TableHead className="font-bold text-[10px] uppercase tracking-widest text-right px-8">Acciones</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {planes.map((plan) => (
                                <TableRow key={plan.id} className="hover:bg-slate-50 dark:hover:bg-white/5 transition-colors border-slate-50 dark:border-white/5">
                                    <TableCell className="font-black text-slate-900 dark:text-white px-8 uppercase tracking-tighter italic">{plan.nombre}</TableCell>
                                    <TableCell>
                                       <Badge variant="outline" className="text-[9px] font-bold border-slate-200 dark:border-white/10">{plan.tipo_usuario_objetivo}</Badge>
                                    </TableCell>
                                    <TableCell className="text-slate-500 font-medium text-xs">{plan.frecuencia}</TableCell>
                                    <TableCell className="font-black text-slate-900 dark:text-white">${parseFloat(plan.precio).toLocaleString()}</TableCell>
                                    <TableCell>
                                        <Badge className={plan.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}>
                                            {plan.is_active ? 'ACTIVO' : 'SUSPENDIDO'}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="text-right px-8">
                                       <div className="flex justify-end gap-1">
                                          <Button variant="ghost" size="sm" className="h-10 w-10 p-0 hover:text-brand" onClick={() => handleOpenModal(plan)}>
                                              <FiEdit size={16} />
                                          </Button>
                                          <Button variant="ghost" size="sm" className="h-10 w-10 p-0 hover:text-red-500" onClick={() => handleDeletePlan(plan.id)}>
                                              <FiTrash2 size={16} />
                                          </Button>
                                       </div>
                                    </TableCell>
                                </TableRow>
                            ))}
                            {planes.length === 0 && !isLoading && (
                               <TableRow>
                                  <TableCell colSpan={6} className="text-center py-24 text-slate-400 font-bold italic">
                                     No hay planes definidos en el sistema soberano.
                                  </TableCell>
                               </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            <PlanFormModal
                isOpen={isModalOpen}
                onClose={handleCloseModal}
                onSave={handleSavePlan}
                planToEdit={planToEdit}
            />
        </div>
    );
}
