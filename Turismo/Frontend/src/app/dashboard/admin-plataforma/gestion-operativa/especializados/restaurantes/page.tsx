"use client";

import { useState } from 'react';
import useSWR from 'swr';
import { PageHeader } from '@/components/shared/page-header';
import { Button } from '@/components/ui/Button';
import { Spinner } from '@/components/common/Spinner'; // Asumo que existe
import { Alert } from '@/components/common/Alert'; // Asumo que existe

// Simulación de tipos
interface RestaurantTable {
    id: number;
    table_number: string;
    capacity: number;
    status: 'FREE' | 'OCCUPIED' | 'RESERVED' | 'DIRTY';
    pos_x: number;
    pos_y: number;
}

const fetcher = (url: string) => apiClient.get(url).then(res => res.data.results);

const statusConfig = {
    FREE: { bg: 'bg-green-500', text: 'Libre' },
    OCCUPIED: { bg: 'bg-red-600', text: 'Ocupada' },
    RESERVED: { bg: 'bg-yellow-500', text: 'Reservada' },
    DIRTY: { bg: 'bg-gray-500', text: 'Sucia' },
};

export default function RestaurantFloorPlanPage() {
    const { data: tables, error, isLoading } = useSWR<RestaurantTable[]>('/api/v1/mi-negocio/gestion-operativa/restaurante/tables/', fetcher);
    const [isEditMode, setIsEditMode] = useState(false);

    if (isLoading) return <Spinner text="Cargando plano del salón..." />;
    if (error) return <Alert type="error" title="Error">No se pudo cargar el plano del salón.</Alert>;

    return (
        <div className="flex flex-col gap-8">
            <PageHeader
                title="Plano de Salón Interactivo"
                description="Gestiona el estado de tus mesas en tiempo real y organiza el layout de tu restaurante."
            >
                <Button onClick={() => setIsEditMode(!isEditMode)}>
                    {isEditMode ? 'Guardar Plano' : 'Editar Plano'}
                </Button>
            </PageHeader>

            <div className="relative w-full h-[75vh] bg-gray-100 border-2 border-dashed rounded-lg">
                {tables?.map(table => (
                    <div
                        key={table.id}
                        className={`absolute w-24 h-24 rounded-lg shadow-lg flex flex-col justify-center items-center text-white font-bold
                                   ${statusConfig[table.status].bg} ${isEditMode ? 'cursor-move' : 'cursor-pointer'}`}
                        style={{ left: `${table.pos_x}px`, top: `${table.pos_y}px` }}
                        // Aquí iría la lógica de Draggable
                    >
                        <span>Mesa {table.table_number}</span>
                        <span className="text-xs font-normal">{statusConfig[table.status].text}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}

// Asumo que existe un cliente de API en @/services/api
import axios from 'axios';
const apiClient = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000',
});
