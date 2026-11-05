import React from 'react';

const PrestadorDashboard = () => {
  return (
    <div className="p-4 border rounded-lg">
      <h2 className="text-xl font-semibold">Estadísticas Rápidas</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
        <div className="p-4 bg-gray-100 rounded-lg">
          <h3 className="font-bold">Reservas Hoy</h3>
          <p className="text-3xl">5</p>
        </div>
        <div className="p-4 bg-gray-100 rounded-lg">
          <h3 className="font-bold">Ingresos del Mes</h3>
          <p className="text-3xl">$1,200</p>
        </div>
        <div className="p-4 bg-gray-100 rounded-lg">
          <h3 className="font-bold">Nuevos Clientes</h3>
          <p className="text-3xl">15</p>
        </div>
      </div>
    </div>
  );
};

export default PrestadorDashboard;