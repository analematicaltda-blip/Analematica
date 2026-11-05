'use client';

import React, { useState, useEffect } from 'react';
import { Users, Plus, ShieldCheck, MapPin, Search } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';

export default function DeliveryRepartidoresPage() {
  const { fetchData } = useMiNegocioApi('delivery/drivers');
  const [drivers, setDrivers] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDrivers();
  }, []);

  const loadDrivers = async () => {
    try {
      const data = await fetchData();
      setDrivers(data || []);
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
          <Users className="h-6 w-6 text-green-600" />
          Gestión de Repartidores
        </h1>
        <button className="bg-green-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-green-700 transition-all shadow-md text-sm font-bold">
           <Plus className="h-4 w-4" /> Registrar Repartidor
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {drivers.length === 0 && !isLoading && (
           <div className="col-span-full p-20 text-center border-2 border-dashed rounded-xl text-gray-400">
             No hay repartidores registrados en este Tenant.
           </div>
        )}
        {drivers.map((driver) => (
          <Card key={driver.id} className="relative overflow-hidden hover:shadow-2xl transition-all border-none bg-white shadow-lg group">
             <div className="absolute top-0 right-0 p-2">
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  driver.is_available ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                }`}>
                  {driver.is_available ? 'DISPONIBLE' : 'OCUPADO'}
                </span>
             </div>
             <CardHeader className="flex flex-row items-center gap-4 pb-2">
                <div className="h-12 w-12 bg-gray-100 rounded-full flex items-center justify-center text-gray-400 font-bold text-lg group-hover:bg-green-100 group-hover:text-green-600 transition-colors">
                  {driver.username?.charAt(0).toUpperCase()}
                </div>
                <div>
                   <CardTitle className="text-base font-bold text-gray-900">{driver.username}</CardTitle>
                   <div className="text-xs text-gray-400">Licencia: {driver.license_number}</div>
                </div>
             </CardHeader>
             <CardContent className="space-y-4">
                <div className="flex justify-between items-center py-2 border-y border-gray-50">
                   <div className="text-center flex-1">
                      <div className="text-lg font-bold text-gray-800">4.9</div>
                      <div className="text-[10px] text-gray-400 uppercase tracking-widest font-bold">Calificación</div>
                   </div>
                   <div className="w-px h-8 bg-gray-100"></div>
                   <div className="text-center flex-1">
                      <div className="text-lg font-bold text-gray-800">1.242</div>
                      <div className="text-[10px] text-gray-400 uppercase tracking-widest font-bold">Viajes</div>
                   </div>
                </div>

                <div className="space-y-2">
                   <div className="flex items-center gap-2 text-sm text-gray-600 bg-gray-50 p-2 rounded-lg">
                      <ShieldCheck className="h-4 w-4 text-green-500" />
                      <span>Antecedentes Verificados</span>
                   </div>
                   <div className="flex items-center gap-2 text-sm text-gray-600 bg-gray-50 p-2 rounded-lg">
                      <MapPin className="h-4 w-4 text-red-500" />
                      <span>Zona: Casco Urbano</span>
                   </div>
                </div>

                <button className="w-full bg-gray-800 text-white py-2 rounded-lg text-sm font-bold opacity-0 group-hover:opacity-100 transform translate-y-2 group-hover:translate-y-0 transition-all">
                  Ver Historial
                </button>
             </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
