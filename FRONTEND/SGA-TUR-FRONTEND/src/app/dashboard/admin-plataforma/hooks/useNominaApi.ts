import useSWR from 'swr';
import { useApi } from '@/services/api';
import { useCallback } from 'react';

// --- Tipos de Datos ---
interface Empleado {
    id: number;
    nombre: string;
    apellido: string;
    identificacion: string;
    email: string;
}
interface Planilla {
    id: number;
    periodo_inicio: string;
    periodo_fin: string;
    total_neto: string;
}

export const useNominaApi = () => {
    const { api } = useApi();
    const fetcher = (url: string) => api.get(url).then(res => res.data);

    // --- Empleados ---
    const { data: empleados, error: empleadosError, mutate: mutateEmpleados } = useSWR('/v1/mi-negocio/nomina/empleados/', fetcher);
    const createEmpleado = useCallback(async (data: Omit<Empleado, 'id'>) => {
        await api.post('/v1/mi-negocio/nomina/empleados/', data);
        mutateEmpleados();
    }, [api, mutateEmpleados]);

    // --- Planillas ---
    const { data: planillas, mutate: mutatePlanillas } = useSWR('/v1/mi-negocio/nomina/planillas/', fetcher);
    const createPlanilla = useCallback(async (data: any) => { // La data de creación es compleja
        await api.post('/v1/mi-negocio/nomina/planillas/', data);
        mutatePlanillas();
    }, [api, mutatePlanillas]);

    return {
        // Empleados
        empleados,
        empleadosLoading: !empleados && !empleadosError,
        empleadosError,
        createEmpleado,

        // Planillas
        planillas,
        planillasLoading: !planillas,
        createPlanilla,
    };
};
