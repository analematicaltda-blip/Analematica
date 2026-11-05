'use client';

import useSWR from 'swr';
import api from '@/services/api';
import { FacturaVenta, PaginatedResponse } from '@/services/api';

const fetcher = (url: string) => api.get(url).then(res => res.data);

export function useComercialApi() {
  const basePath = '/admin/plataforma/comercial/facturas-venta/';

  const { data, error, isLoading } = useSWR<PaginatedResponse<FacturaVenta>>(basePath, fetcher);

  return {
    facturas: data?.results || [],
    isLoading,
    isError: error,
  };
}
