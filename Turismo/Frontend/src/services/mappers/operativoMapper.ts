export const operativoMapper = {
  mapReservaToUI: (reserva: any) => ({
    id: reserva.id,
    client: reserva.cliente_nombre,
    service: reserva.servicio_nombre,
    date: new Date(reserva.fecha_reserva).toLocaleDateString(),
    status: reserva.estado,
    color: reserva.estado === 'CONFIRMED' ? 'green' : 'amber'
  }),

  mapSSTToUI: (incident: any) => ({
    id: incident.id,
    type: incident.tipo_riesgo,
    level: incident.nivel_severidad,
    date: new Date(incident.fecha_reporte).toLocaleDateString(),
    status: incident.estado_resolucion
  })
};
