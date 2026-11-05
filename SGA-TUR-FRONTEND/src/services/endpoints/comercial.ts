import httpClient from '../index';

export const comercialEndpoints = {
  getFunnels: () => httpClient.get('/v1/mi-negocio/comercial/funnels/'),
  getLeads: () => httpClient.get('/v1/mi-negocio/comercial/leads/'),
  getFacturasVenta: () => httpClient.get('/v1/mi-negocio/comercial/facturas-venta/'),
  createFacturaVenta: (data: any) => httpClient.post('/v1/mi-negocio/comercial/facturas-venta/', data),
  getMarketingCampaigns: () => httpClient.get('/v1/mi-negocio/comercial/marketing/campaigns/'),
};
