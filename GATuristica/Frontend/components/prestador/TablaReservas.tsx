import React from 'react';

const reservas = [
  { id: 1, cliente: 'Juan Pérez', servicio: 'Habitación Doble', fecha: '2025-10-15', estado: 'Confirmada' },
  { id: 2, cliente: 'Ana Gómez', servicio: 'Tour Guiado', fecha: '2025-10-16', estado: 'Pendiente' },
  { id: 3, cliente: 'Luis Torres', servicio: 'Habitación Sencilla', fecha: '2025-10-18', estado: 'Cancelada' },
];

const TablaReservas = () => {
  return (
    <div className="p-4 border rounded-lg">
      <h2 className="text-xl font-semibold mb-4">Últimas Reservas</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white">
          <thead>
            <tr>
              <th className="py-2 px-4 border-b">Cliente</th>
              <th className="py-2 px-4 border-b">Servicio</th>
              <th className="py-2 px-4 border-b">Fecha</th>
              <th className="py-2 px-4 border-b">Estado</th>
            </tr>
          </thead>
          <tbody>
            {reservas.map((reserva) => (
              <tr key={reserva.id}>
                <td className="py-2 px-4 border-b">{reserva.cliente}</td>
                <td className="py-2 px-4 border-b">{reserva.servicio}</td>
                <td className="py-2 px-4 border-b">{reserva.fecha}</td>
                <td className="py-2 px-4 border-b">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    reserva.estado === 'Confirmada' ? 'bg-green-100 text-green-800' :
                    reserva.estado === 'Pendiente' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {reserva.estado}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TablaReservas;