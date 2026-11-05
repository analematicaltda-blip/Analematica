'use client';

import React, { useState, useEffect } from 'react';
import { Map, Navigation, MapPin, Search, Filter } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';

export default function DeliveryRutasPage() {
  const { fetchData } = useMiNegocioApi('delivery/rutas');
  const [rutas, setRutas] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadRutas();
  }, []);

  const loadRutas = async () => {
    try {
      const data = await fetchData();
      setRutas(data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold flex items-center gap-2 text-gray-800">
          <Map className="h-6 w-6 text-emerald-600" />
          Optimización de Rutas
        </h1>
        <button className="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-bold shadow-lg hover:bg-emerald-700 transition-all flex items-center gap-2">
           <Navigation className="h-4 w-4" /> Generar Rutas Hoy
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
         <div className="lg:col-span-1 space-y-4">
            {rutas.length === 0 && !isLoading && (
              <p className="text-gray-400 italic p-4 border rounded-lg">No hay rutas calculadas para hoy.</p>
            )}
            {rutas.map((ruta) => (
               <Card key={ruta.id} className="cursor-pointer hover:border-emerald-500 border-2 transition-all">
                  <CardHeader className="p-4 pb-2 flex flex-row justify-between">
                     <CardTitle className="text-base font-bold">{ruta.nombre}</CardTitle>
                     <span className="text-[10px] bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded font-black uppercase">Activa</span>
                  </CardHeader>
                  <CardContent className="p-4 pt-0 space-y-2 text-sm text-gray-600">
                     <div className="flex items-center gap-2">
                        <MapPin className="h-3 w-3 text-red-500" />
                        <span>Zona: {ruta.zona}</span>
                     </div>
                     <div className="flex justify-between items-center bg-gray-50 p-2 rounded">
                        <span className="text-xs">Tiempo Estimado:</span>
                        <span className="font-bold text-gray-800">{ruta.tiempo_estimado_mins} min</span>
                     </div>
                  </CardContent>
               </Card>
            ))}
         </div>

         <Card className="lg:col-span-2 border-none shadow-2xl bg-gray-100 min-h-[500px] relative overflow-hidden flex items-center justify-center">
            <div className="absolute inset-0 bg-[url('https://maps.googleapis.com/maps/api/staticmap?center=4.312,-73.123&zoom=14&size=800x600&key=MOCK_KEY')] bg-cover opacity-50"></div>
            <div className="relative z-10 text-center space-y-4 bg-white/80 backdrop-blur p-10 rounded-3xl border border-white shadow-2xl">
               <Navigation className="h-12 w-12 text-blue-600 mx-auto animate-bounce" />
               <h3 className="text-xl font-black text-gray-900">Motor de Geolocalización</h3>
               <p className="text-gray-500 max-w-sm">Visualizando rutas optimizadas en tiempo real para Puerto Gaitán.</p>
               <div className="flex justify-center gap-4">
                  <div className="text-center">
                     <div className="text-lg font-bold">12</div>
                     <div className="text-[10px] uppercase text-gray-400 font-bold">Puntos Control</div>
                  </div>
                  <div className="text-center">
                     <div className="text-lg font-bold">5.4km</div>
                     <div className="text-[10px] uppercase text-gray-400 font-bold">Recorrido Total</div>
                  </div>
               </div>
            </div>
         </Card>
      </div>
    </div>
  );
}
