import useSWR from 'swr';
import { useApi } from '@/services/api';
import { useCallback } from 'react';

// --- Tipos de Datos ---
interface CategoriaActivo { id: number; nombre: string; }
interface ActivoFijo {
    id: number;
    nombre: string;
    categoria: number;
    categoria_nombre: string;
    fecha_adquisicion: string;
    valor_adquisicion: string;
    vida_util_meses: number;
    valor_residual: string;
    valor_en_libros: string;
}
interface Depreciacion {
    id: number;
    activo: number;
    fecha: string;
    valor: string;
}

export const useActivosApi = () => {
    const { api } = useApi();
    const fetcher = (url: string) => api.get(url).then(res => res.data);

    // --- Categorías de Activos ---
    const { data: categorias, mutate: mutateCategorias } = useSWR('/v1/mi-negocio/activos/categorias/', fetcher);
    const createCategoria = useCallback(async (data: Omit<CategoriaActivo, 'id'>) => {
        await api.post('/v1/mi-negocio/activos/categorias/', data);
        mutateCategorias();
    }, [api, mutateCategorias]);

    // --- Activos Fijos ---
    const { data: activos, error: activosError, mutate: mutateActivos } = useSWR('/v1/mi-negocio/activos/activos-fijos/', fetcher);
    const createActivo = useCallback(async (data: Omit<ActivoFijo, 'id' | 'categoria_nombre' | 'valor_en_libros'>) => {
        await api.post('/v1/mi-negocio/activos/activos-fijos/', data);
        mutateActivos();
    }, [api, mutateActivos]);

    // --- Depreciaciones ---
    const { data: depreciaciones, mutate: mutateDepreciaciones } = useSWR('/v1/mi-negocio/activos/depreciaciones/', fetcher);
    const createDepreciacion = useCallback(async (data: Omit<Depreciacion, 'id'>) => {
        await api.post('/v1/mi-negocio/activos/depreciaciones/', data);
        mutateDepreciaciones();
        mutateActivos(); // Revalidar activos para actualizar valor en libros
    }, [api, mutateDepreciaciones, mutateActivos]);

    return {
        // Categorías
        categorias,
        categoriasLoading: !categorias,
        createCategoria,

        // Activos Fijos
        activos,
        activosLoading: !activos && !activosError,
        activosError,
        createActivo,

        // Depreciaciones
        depreciaciones,
        depreciacionesLoading: !depreciaciones,
        createDepreciacion,
    };
};
