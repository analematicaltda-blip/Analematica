'use client';

import useSWR from 'swr';
import api from '@/services/api';
import { FacturaVenta, PaginatedResponse } from '@/services/api';

const fetcher = (url: string) => api.get(url).then(res => res.data);

export function useComercialApi() {
  const basePath = '/v1/mi-negocio/comercial/facturas-venta/';

  const { data, error, isLoading } = useSWR<PaginatedResponse<FacturaVenta>>(basePath, fetcher);

  const sendDian = async (id: string) => {
    return api.post(`${basePath}${id}/send-dian/`);
  };

  const getDianStatus = async (id: string) => {
    return api.get(`${basePath}${id}/dian-status/`);
  };

  return {
    facturas: data?.results || [],
    isLoading,
    isError: error,
    sendDian,
    getDianStatus
  };
}
