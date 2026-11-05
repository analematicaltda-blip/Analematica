import React from 'react';

const facturas = [
  { id: 'F-001', cliente: 'Juan Pérez', monto: 150.00, fecha: '2025-10-15' },
  { id: 'F-002', cliente: 'Ana Gómez', monto: 50.00, fecha: '2025-10-16' },
];

const PanelFacturacion = () => {
  return (
    <div className="p-4 border rounded-lg">
      <h2 className="text-xl font-semibold mb-4">Facturación</h2>
      <button className="mb-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
        Crear Nueva Factura
      </button>
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white">
          <thead>
            <tr>
              <th className="py-2 px-4 border-b">ID Factura</th>
              <th className="py-2 px-4 border-b">Cliente</th>
              <th className="py-2 px-4 border-b">Monto</th>
              <th className="py-2 px-4 border-b">Fecha</th>
              <th className="py-2 px-4 border-b">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {facturas.map((factura) => (
              <tr key={factura.id}>
                <td className="py-2 px-4 border-b">{factura.id}</td>
                <td className="py-2 px-4 border-b">{factura.cliente}</td>
                <td className="py-2 px-4 border-b">${factura.monto.toFixed(2)}</td>
                <td className="py-2 px-4 border-b">{factura.fecha}</td>
                <td className="py-2 px-4 border-b">
                  <button className="text-blue-600 hover:underline">Descargar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PanelFacturacion;