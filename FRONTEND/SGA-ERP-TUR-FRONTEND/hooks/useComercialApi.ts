import useSWR from 'swr';
import { useApi } from '@/services/api';
import { useCallback } from 'react';

// --- Tipos de Datos ---
interface ItemFactura {
    id?: number;
    producto?: number;
    descripcion: string;
    cantidad: number;
    precio_unitario: number;
    impuestos?: number;
}

interface FacturaVenta {
    id: number;
    cliente: { id: number; nombre: string; };
    number: string;
    issue_date: string;
    total: string;
    estado: string;
    items: ItemFactura[];
}

interface ReciboCaja {
    id: number;
    factura: number;
    fecha_pago: string;
    monto: string;
    metodo_pago: string;
}

export const useComercialApi = () => {
    const { api } = useApi();
    const fetcher = (url: string) => api.get(url).then(res => res.data);

    // --- Facturas de Venta ---
    const { data: facturas, error: facturasError, mutate: mutateFacturas } = useSWR('/v1/mi-negocio/comercial/facturas-venta/', fetcher);

    const createFactura = useCallback(async (data: { cliente_id: number; number: string; issue_date: string; fecha_vencimiento?: string; items: ItemFactura[] }) => {
        await api.post('/v1/mi-negocio/comercial/facturas-venta/', data);
        mutateFacturas();
    }, [api, mutateFacturas]);

    // --- Recibos de Caja ---
    const { data: recibos, mutate: mutateRecibos } = useSWR('/v1/mi-negocio/comercial/recibos-caja/', fetcher);

    const createRecibo = useCallback(async (data: Omit<ReciboCaja, 'id'>) => {
        await api.post('/v1/mi-negocio/comercial/recibos-caja/', data);
        mutateRecibos();
        mutateFacturas(); // Revalidar facturas para actualizar estado de pago
    }, [api, mutateRecibos, mutateFacturas]);

    return {
        // Facturas de Venta
        facturas,
        facturasLoading: !facturas && !facturasError,
        facturasError,
        createFactura,

        // Recibos de Caja
        recibos,
        recibosLoading: !recibos,
        createRecibo,
    };
};
