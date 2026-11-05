import useSWR from 'swr';
import { useApi } from '@/services/api';
import { useCallback } from 'react';

// --- Tipos de Datos ---
interface Proyecto {
    id: number;
    nombre: string;
    descripcion: string;
    fecha_inicio: string;
    fecha_fin?: string;
    presupuesto: string;
    estado: string;
    total_ingresos: string;
    total_costos: string;
    rentabilidad: string;
}

export const useProyectosApi = () => {
    const { api } = useApi();
    const fetcher = (url: string) => api.get(url).then(res => res.data);

    // --- Proyectos ---
    const { data: proyectos, error: proyectosError, mutate: mutateProyectos } = useSWR('/mi-negocio/proyectos/proyectos/', fetcher);

    const createProyecto = useCallback(async (data: Omit<Proyecto, 'id' | 'total_ingresos' | 'total_costos' | 'rentabilidad'>) => {
        await api.post('/mi-negocio/proyectos/proyectos/', data);
        mutateProyectos();
    }, [api, mutateProyectos]);

    // Aquí se podrían agregar hooks para Ingresos y Costos si se gestionan individualmente

    return {
        proyectos,
        proyectosLoading: !proyectos && !proyectosError,
        proyectosError,
        createProyecto,
    };
};
