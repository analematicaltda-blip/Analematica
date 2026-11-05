'use client';

import React, { useState, useEffect } from 'react';
import { Package, Search, Filter, ArrowRight, Truck } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';

export default function DeliveryPedidosPage() {
  const { fetchData, postData } = useMiNegocioApi('delivery/services');
  const [pedidos, setPedidos] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadPedidos();
  }, []);

  const loadPedidos = async () => {
    try {
      const data = await fetchData();
      setPedidos(data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAssign = async (pedidoId: string) => {
    try {
      await postData(`${pedidoId}/assign/`, {});
      loadPedidos();
    } catch (e) {
      alert("No hay repartidores disponibles.");
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold flex items-center gap-2 text-gray-800">
          <Package className="h-6 w-6 text-blue-600" />
          Gestión de Pedidos para Entrega
        </h1>
        <div className="flex gap-2">
           <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-gray-50 transition-all shadow-sm text-sm">
             <Filter className="h-4 w-4" /> Filtros
           </button>
        </div>
      </div>

      <Card className="shadow-xl border-none">
        <CardHeader className="bg-gradient-to-r from-gray-800 to-gray-700 text-white rounded-t-lg py-4">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por ID, cliente o dirección..."
              className="pl-10 pr-4 py-2 bg-gray-100/10 border-gray-600 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 w-full placeholder-gray-400"
            />
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-gray-50 text-gray-500 uppercase text-xs">
                <tr>
                  <th className="p-4">ID / Prioridad</th>
                  <th className="p-4">Origen / Destino</th>
                  <th className="p-4">Tarifa</th>
                  <th className="p-4">Estado</th>
                  <th className="p-4 text-center">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 bg-white">
                {pedidos.length === 0 && !isLoading && (
                  <tr>
                    <td colSpan={5} className="p-10 text-center text-gray-400 italic">No hay pedidos registrados para entrega.</td>
                  </tr>
                )}
                {pedidos.map((pedido) => (
                  <tr key={pedido.id} className="hover:bg-blue-50/30 transition-colors group">
                    <td className="p-4">
                      <div className="font-bold text-gray-900">#{pedido.id.substring(0,8)}</div>
                      <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                        pedido.prioridad === 'ALTA' ? 'bg-red-100 text-red-600' : 'bg-blue-100 text-blue-600'
                      }`}>
                        {pedido.prioridad}
                      </span>
                    </td>
                    <td className="p-4">
                      <div className="text-xs text-gray-400 flex items-center gap-1">
                        <span className="w-1.5 h-1.5 bg-gray-300 rounded-full"></span> {pedido.origin_address}
                      </div>
                      <div className="text-sm font-medium text-gray-700 flex items-center gap-1">
                        <ArrowRight className="h-3 w-3 text-blue-500" /> {pedido.destination_address}
                      </div>
                    </td>
                    <td className="p-4 font-mono font-bold text-green-600">
                      ${Number(pedido.estimated_price).toLocaleString()}
                    </td>
                    <td className="p-4">
                      <span className={`px-2 py-1 rounded-full text-[10px] font-bold ${
                        pedido.status === 'PENDIENTE' ? 'bg-gray-100 text-gray-600' :
                        pedido.status === 'EN_RUTA' ? 'bg-orange-100 text-orange-600 animate-pulse' :
                        pedido.status === 'ENTREGADO' ? 'bg-green-100 text-green-600' : 'bg-blue-100 text-blue-600'
                      }`}>
                        {pedido.status}
                      </span>
                    </td>
                    <td className="p-4 text-center">
                       {pedido.status === 'PENDIENTE' ? (
                         <button
                            onClick={() => handleAssign(pedido.id)}
                            className="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-xs font-semibold hover:bg-blue-700 shadow-sm flex items-center gap-2 mx-auto"
                         >
                           <Truck className="h-3 w-3" /> Asignar Repartidor
                         </button>
                       ) : (
                         <button className="text-gray-400 hover:text-blue-600 transition-colors">
                           Detalles
                         </button>
                       )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
