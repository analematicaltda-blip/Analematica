"use client";

import React, { useState, useEffect, useCallback } from 'react';
import api from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { FiTruck, FiMapPin, FiCheckCircle, FiClock, FiDollarSign } from 'react-icons/fi';
import { ViewState } from '@/components/ui/ViewState';
import { toast } from 'react-toastify';

export default function DeliveryDashboardPage() {
  const { token, user } = useAuth();
  const [services, setServices] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchServices = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const response = await api.get('/v1/operations/delivery/services/');
      setServices(response.data.results || []);
    } catch (err) {
      setError("Error al cargar servicios asignados.");
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchServices();
  }, [fetchServices]);

  const handleComplete = async (id: string) => {
    try {
      await api.post(`/v1/operations/delivery/services/${id}/complete_service/`);
      toast.success("Servicio completado. Pago procesado institucionalmente.");
      fetchServices();
    } catch (err) {
      toast.error("Error al completar el servicio.");
    }
  };

  const activeServices = services.filter(s => s.status !== 'COMPLETED');
  const completedServices = services.filter(s => s.status === 'COMPLETED');

  return (
    <div className="p-8 space-y-8 bg-slate-50 min-h-screen">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Panel Logístico</h1>
          <p className="text-slate-500 font-medium">Gestión de entregas y servicios de transporte.</p>
        </div>
        <div className="bg-indigo-600 text-white px-4 py-2 rounded-xl text-xs font-black flex items-center gap-2">
           <FiTruck /> {user?.username} (Socio Logístico)
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="space-y-6">
           <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest ml-4">Servicios Activos</h3>
           <ViewState isLoading={isLoading} error={error} isEmpty={activeServices.length === 0}>
              {activeServices.map(service => (
                <div key={service.id} className="bg-white p-8 rounded-[2.5rem] shadow-xl border border-slate-100 space-y-6">
                   <div className="flex justify-between items-start">
                      <span className="bg-amber-100 text-amber-700 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest">
                         {service.status}
                      </span>
                      <p className="text-xl font-black text-slate-900">${service.estimated_price} COP</p>
                   </div>

                   <div className="space-y-4">
                      <div className="flex gap-4">
                         <div className="w-8 h-8 bg-indigo-50 text-indigo-500 rounded-xl flex items-center justify-center shrink-0">
                            <FiMapPin size={16} />
                         </div>
                         <div>
                            <p className="text-[9px] font-black text-slate-400 uppercase">Recoger en</p>
                            <p className="text-sm font-bold text-slate-900">{service.origin_address}</p>
                         </div>
                      </div>
                      <div className="flex gap-4">
                         <div className="w-8 h-8 bg-red-50 text-red-500 rounded-xl flex items-center justify-center shrink-0">
                            <FiMapPin size={16} />
                         </div>
                         <div>
                            <p className="text-[9px] font-black text-slate-400 uppercase">Entregar en</p>
                            <p className="text-sm font-bold text-slate-900">{service.destination_address}</p>
                         </div>
                      </div>
                   </div>

                   <button
                      onClick={() => handleComplete(service.id)}
                      className="w-full bg-slate-900 hover:bg-slate-800 text-white py-4 rounded-2xl font-black uppercase tracking-widest text-xs transition-all flex items-center justify-center gap-2"
                   >
                      <FiCheckCircle /> Marcar como Completado
                   </button>
                </div>
              ))}
           </ViewState>
        </div>

        <div className="space-y-6">
           <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest ml-4">Historial Reciente</h3>
           <div className="bg-white rounded-[2.5rem] border border-slate-100 shadow-sm overflow-hidden">
              <table className="w-full text-left">
                 <tbody className="divide-y divide-slate-50">
                    {completedServices.slice(0, 5).map(service => (
                       <tr key={service.id}>
                          <td className="px-8 py-6">
                             <p className="text-xs font-bold text-slate-900">{service.destination_address}</p>
                             <p className="text-[10px] text-slate-400 flex items-center gap-1 font-medium">
                                <FiClock /> {new Date(service.updated_at).toLocaleDateString()}
                             </p>
                          </td>
                          <td className="px-8 py-6 text-right">
                             <div className="flex items-center justify-end gap-1 text-green-600 font-black text-sm">
                                <FiDollarSign size={14} /> {service.final_price}
                             </div>
                             <p className="text-[9px] font-black text-slate-400 uppercase tracking-tighter">Pago Liquidado</p>
                          </td>
                       </tr>
                    ))}
                    {completedServices.length === 0 && (
                       <tr>
                          <td className="px-8 py-10 text-center text-slate-400 font-medium text-xs">No hay servicios completados aún.</td>
                       </tr>
                    )}
                 </tbody>
              </table>
           </div>
        </div>
      </div>
    </div>
  );
}
