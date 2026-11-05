'use client';

import React, { useState, useEffect } from 'react';
import { Truck, Send, AlertTriangle, CheckCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';

export default function DeliveryDespachoPage() {
  const { fetchData, postData } = useMiNegocioApi('delivery/services');
  const [pedidos, setPedidos] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadPedidos();
  }, []);

  const loadPedidos = async () => {
    try {
      const data = await fetchData();
      setPedidos(data?.filter((p: any) => p.status === 'LISTO_DESPACHO' || p.status === 'EN_RUTA') || []);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStart = async (id: string) => {
    await postData(`${id}/start/`, {});
    loadPedidos();
  };

  const handleComplete = async (id: string) => {
    await postData(`${id}/complete/`, {
        firma: "FIRMA_DIGITAL_OK",
        observaciones: "Entrega exitosa sin novedades",
        latitud: 4.312,
        longitud: -73.123
    });
    loadPedidos();
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold flex items-center gap-2 text-gray-800">
        <Send className="h-6 w-6 text-orange-600" />
        Panel de Despacho y Control
      </h1>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <Card className="border-none shadow-lg">
          <CardHeader className="bg-orange-50 text-orange-800 border-b border-orange-100 rounded-t-lg">
            <CardTitle className="text-sm font-black uppercase tracking-widest flex items-center gap-2">
              <Truck className="h-4 w-4" /> Pendientes de Despacho
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
             <div className="divide-y divide-gray-100">
                {pedidos.filter(p => p.status === 'LISTO_DESPACHO').map((p) => (
                  <div key={p.id} className="p-4 hover:bg-gray-50 flex justify-between items-center group">
                     <div className="space-y-1">
                        <div className="font-bold text-gray-900 text-sm">#{p.id.substring(0,8)}</div>
                        <div className="text-xs text-gray-500">{p.destination_address}</div>
                        <div className="text-[10px] text-gray-400">Repartidor: {p.driver_name || 'Sin asignar'}</div>
                     </div>
                     <button
                        onClick={() => handleStart(p.id)}
                        className="bg-orange-600 text-white px-4 py-1.5 rounded-lg text-xs font-bold hover:bg-orange-700 transition-all opacity-0 group-hover:opacity-100 shadow-md"
                     >
                        Despachar
                     </button>
                  </div>
                ))}
                {pedidos.filter(p => p.status === 'LISTO_DESPACHO').length === 0 && (
                   <div className="p-8 text-center text-gray-400 italic text-sm">No hay pedidos listos para despachar.</div>
                )}
             </div>
          </CardContent>
        </Card>

        <Card className="border-none shadow-lg">
          <CardHeader className="bg-blue-50 text-blue-800 border-b border-blue-100 rounded-t-lg">
            <CardTitle className="text-sm font-black uppercase tracking-widest flex items-center gap-2">
              <Truck className="h-4 w-4 animate-bounce" /> En Ruta Actualmente
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
             <div className="divide-y divide-gray-100">
                {pedidos.filter(p => p.status === 'EN_RUTA').map((p) => (
                  <div key={p.id} className="p-4 hover:bg-gray-50 flex justify-between items-center group">
                     <div className="space-y-1">
                        <div className="font-bold text-gray-900 text-sm">#{p.id.substring(0,8)}</div>
                        <div className="text-xs text-gray-500">{p.destination_address}</div>
                        <div className="text-[10px] text-orange-600 font-bold">Tiempo estimado: 15 min</div>
                     </div>
                     <button
                        onClick={() => handleComplete(p.id)}
                        className="bg-green-600 text-white px-4 py-1.5 rounded-lg text-xs font-bold hover:bg-green-700 transition-all opacity-0 group-hover:opacity-100 shadow-md flex items-center gap-2"
                     >
                        <CheckCircle className="h-3 w-3" /> Confirmar Entrega
                     </button>
                  </div>
                ))}
                {pedidos.filter(p => p.status === 'EN_RUTA').length === 0 && (
                   <div className="p-8 text-center text-gray-400 italic text-sm">No hay pedidos en ruta.</div>
                )}
             </div>
          </CardContent>
        </Card>
      </div>

      <div className="bg-gray-100 p-4 rounded-xl border border-gray-200 flex items-center justify-between">
         <div className="flex items-center gap-3">
            <div className="h-10 w-10 bg-yellow-100 rounded-full flex items-center justify-center">
               <AlertTriangle className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
               <div className="font-bold text-gray-800">Alertas Logísticas</div>
               <div className="text-xs text-gray-500">2 pedidos con retraso en Zona Sur</div>
            </div>
         </div>
         <button className="text-blue-600 font-bold text-sm">Ver Centro de Alertas</button>
      </div>
    </div>
  );
}
