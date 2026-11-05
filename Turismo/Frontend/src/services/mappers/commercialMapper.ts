export const commercialMapper = {
  mapLeadToUI: (lead: any) => ({
    id: lead.id,
    name: lead.full_name,
    status: lead.status === 'NEW' ? 'Nuevo' : lead.status,
    value: lead.estimated_value,
    color: lead.status === 'NEW' ? 'blue' : 'gray'
  }),

  mapFacturaToUI: (factura: any) => ({
    id: factura.id,
    code: factura.number,
    client: factura.cliente_nombre,
    date: new Date(factura.issue_date).toLocaleDateString(),
    total: `$${parseFloat(factura.total).toLocaleString()}`,
    status: factura.estado_display
  })
};
