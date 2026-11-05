import useSWR from 'swr';
import { useApi } from '@/services/api';
import { useCallback } from 'react';

// Tipos para los datos
interface Proveedor {
    id: number;
    nombre: string;
    identificacion?: string;
    telefono?: string;
    email?: string;
    direccion?: string;
}

interface FacturaCompra {
    id: number;
    proveedor: number;
    proveedor_nombre: string;
    number: string;
    issue_date: string;
    fecha_vencimiento?: string;
    subtotal: string;
    impuestos: string;
    total: string;
    estado: string;
    notas?: string;
}

export const useComprasApi = () => {
    const { api } = useApi();
    const fetcher = (url: string) => api.get(url).then(res => res.data);

    // --- Proveedores ---
    const { data: proveedores, error: proveedoresError, mutate: mutateProveedores } = useSWR('/v1/mi-negocio/compras/proveedores/', fetcher);

    const createProveedor = useCallback(async (data: Omit<Proveedor, 'id'>) => {
        const response = await api.post('/v1/mi-negocio/compras/proveedores/', data);
        mutateProveedores();
        return response.data;
    }, [api, mutateProveedores]);

    const updateProveedor = useCallback(async (id: number, data: Omit<Proveedor, 'id'>) => {
        const response = await api.put(`/v1/mi-negocio/compras/proveedores/${id}/`, data);
        mutateProveedores();
        return response.data;
    }, [api, mutateProveedores]);

    const deleteProveedor = useCallback(async (id: number) => {
        await api.delete(`/v1/mi-negocio/compras/proveedores/${id}/`);
        mutateProveedores();
    }, [api, mutateProveedores]);


    // --- Facturas de Compra ---
    const { data: facturasCompra, error: facturasCompraError, mutate: mutateFacturasCompra } = useSWR('/v1/mi-negocio/compras/facturas/', fetcher);

    const createFacturaCompra = useCallback(async (data: Omit<FacturaCompra, 'id' | 'proveedor_nombre'>) => {
        const response = await api.post('/v1/mi-negocio/compras/facturas/', data);
        mutateFacturasCompra();
        return response.data;
    }, [api, mutateFacturasCompra]);

    // Aquí se podrían agregar update y delete para facturas si la lógica de negocio lo permite

    const generarPagoMasivo = useCallback(async (factura_ids: number[]) => {
        const response = await api.post('/v1/mi-negocio/compras/generar-pago-masivo/', { factura_ids }, {
            responseType: 'blob', // Importante para manejar la descarga de archivos
        });

        // Crear un enlace para descargar el archivo
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'pagos_masivos.csv');
        document.body.appendChild(link);
        link.click();
        link.parentNode?.removeChild(link);

    }, [api]);

    return {
        // Proveedores
        proveedores,
        proveedoresLoading: !proveedores && !proveedoresError,
        proveedoresError,
        createProveedor,
        updateProveedor,
        deleteProveedor,

        // Facturas de Compra
        facturasCompra,
        facturasCompraLoading: !facturasCompra && !facturasCompraError,
        facturasCompraError,
        createFacturaCompra,
        generarPagoMasivo,
    };
};
