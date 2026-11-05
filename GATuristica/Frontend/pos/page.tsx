import React from 'react';
import { WebLayout, KpiCard, Button, DataTable } from '@sarita/shared-ui';

export default function WebPOSPage() {
  return (
    <WebLayout>
      <div className="flex justify-between items-center mb-10">
        <h1 className="text-3xl font-bold">Punto de Venta (Web POS)</h1>
        <Button variant="outline">Abrir Caja</Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-white p-8 rounded-3xl shadow-sm border border-slate-100">
          <h2 className="text-xl font-bold mb-6">Selección de Servicios</h2>
          <DataTable
            columns={[{header: 'Servicio', accessor: 'n'}, {header: 'Precio', accessor: 'p'}]}
            data={[{n: 'Tour del Manatí', p: '5'}, {n: 'Hospedaje Noche', p: '20'}]}
          />
        </div>
        <div className="bg-slate-900 text-white p-8 rounded-3xl shadow-xl">
          <h2 className="text-xl font-bold mb-6 text-white">Resumen de Venta</h2>
          <div className="space-y-4 mb-8">
            <div className="flex justify-between"><span>Subtotal</span><span>-bash.00</span></div>
            <div className="flex justify-between font-bold text-2xl"><span>Total</span><span>-bash.00</span></div>
          </div>
          <Button className="w-full bg-primary py-4">Procesar Pago</Button>
        </div>
      </div>
    </WebLayout>
  );
}
