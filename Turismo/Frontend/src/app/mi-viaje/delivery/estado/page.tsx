"use client";

import React, { useState, useEffect, useCallback, Suspense } from 'react';
import api from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { FiClock, FiUser, FiTruck, FiCheckCircle, FiShield, FiRotateCw, FiExternalLink } from 'react-icons/fi';
import { useRouter, useSearchParams } from 'next/navigation';
import { ViewState } from '@/components/ui/ViewState';

function DeliveryStatusContent() {
  const { token } = useAuth();
  const searchParams = useSearchParams();
  const serviceId = searchParams.get('id');
  const [service, setService] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    if (!token || !serviceId) return;
    try {
      const response = await api.get(`/delivery/services/${serviceId}/`);
      setService(response.data);
    } catch (err) {
      setError("No se pudo cargar el estado del servicio.");
    } finally {
      setIsLoading(false);
    }
  }, [token, serviceId]);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 10000); // Polling cada 10s
    return () => clearInterval(interval);
  }, [fetchStatus]);

  if (!serviceId) return <ViewState error="ID de servicio no proporcionado." />;

  return (
    <div className="min-h-screen bg-slate-50 py-12 px-4">
      <div className="max-w-3xl mx-auto space-y-8">
        <div className="flex items-center justify-between">
           <h1 className="text-3xl font-black text-slate-900 tracking-tight">Estado del Servicio</h1>
           <button onClick={fetchStatus} className="p-3 bg-white rounded-2xl shadow-sm hover:bg-slate-50 transition-colors">
              <FiRotateCw className={isLoading ? 'animate-spin' : ''} />
           </button>
        </div>

        <ViewState isLoading={isLoading} error={error}>
           <div className="bg-white rounded-[2.5rem] overflow-hidden shadow-xl border border-slate-100">
              <div className="bg-indigo-600 p-10 text-white flex justify-between items-center">
                 <div>
                    <p className="text-indigo-100 text-[10px] font-black uppercase tracking-widest mb-2">Estatus Actual</p>
                    <h2 className="text-4xl font-black">{service?.status}</h2>
                 </div>
                 <div className="w-20 h-20 bg-white/10 rounded-3xl flex items-center justify-center backdrop-blur-md">
                    {service?.status === 'REQUESTED' && <FiClock size={40} />}
                    {service?.status === 'ASSIGNED' && <FiUser size={40} />}
                    {service?.status === 'IN_PROGRESS' && <FiTruck size={40} />}
                    {service?.status === 'COMPLETED' && <FiCheckCircle size={40} />}
                 </div>
              </div>

              <div className="p-10 space-y-10">
                 {/* Línea de Tiempo de Gobernanza */}
                 <div className="space-y-6">
                    <div className="flex gap-4">
                       <div className="flex flex-col items-center">
                          <div className={`w-4 h-4 rounded-full ${service?.status ? 'bg-indigo-600' : 'bg-slate-200'}`}></div>
                          <div className="w-0.5 h-full bg-slate-100"></div>
                       </div>
                       <div>
                          <p className="font-bold text-slate-900">Solicitud Recibida</p>
                          <p className="text-xs text-slate-500">{new Date(service?.created_at).toLocaleString()}</p>
                       </div>
                    </div>

                    {service?.driver && (
                       <div className="flex gap-4">
                          <div className="flex flex-col items-center">
                             <div className="w-4 h-4 rounded-full bg-indigo-600"></div>
                             <div className="w-0.5 h-full bg-slate-100"></div>
                          </div>
                          <div>
                             <p className="font-bold text-slate-900">Conductor Asignado</p>
                             <p className="text-sm text-slate-600">{service.driver.username}</p>
                          </div>
                       </div>
                    )}

                    <div className="flex gap-4">
                       <div className="flex flex-col items-center">
                          <div className={`w-4 h-4 rounded-full ${service?.status === 'COMPLETED' ? 'bg-green-500' : 'bg-slate-200'}`}></div>
                       </div>
                       <div>
                          <p className="font-bold text-slate-900">Entrega / Destino</p>
                          <p className="text-sm text-slate-600">{service?.destination_address}</p>
                       </div>
                    </div>
                 </div>

                 {/* Orden Operativa Vinculada (Interoperabilidad FASE 9) */}
                 {service?.related_operational_order_id && (
                    <div className="bg-indigo-50 p-8 rounded-3xl border border-indigo-100 flex items-center justify-between group">
                       <div className="flex items-center gap-6">
                          <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center text-indigo-600 shadow-sm">
                             <FiCheckCircle size={32} />
                          </div>
                          <div>
                             <p className="text-[10px] font-black text-indigo-400 uppercase tracking-widest">Servicio Especializado Vinculado</p>
                             <p className="text-xl font-black text-indigo-900">Orden Operativa</p>
                             <p className="text-xs font-mono font-bold text-indigo-400 truncate w-32">{service.related_operational_order_id}</p>
                          </div>
                       </div>
                       <button className="p-4 bg-white text-indigo-600 rounded-2xl shadow-sm opacity-0 group-hover:opacity-100 transition-all transform translate-x-4 group-hover:translate-x-0">
                          <FiExternalLink />
                       </button>
                    </div>
                 )}

                 {/* Detalles del Vehículo */}
                 {service?.vehicle && (
                    <div className="bg-slate-50 p-8 rounded-3xl border border-slate-100 flex items-center gap-6">
                       <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center text-indigo-600 shadow-sm">
                          <FiTruck size={32} />
                       </div>
                       <div>
                          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Vehículo Identificado</p>
                          <p className="text-xl font-black text-slate-900">{service.vehicle.plate}</p>
                          <p className="text-xs font-bold text-indigo-600 uppercase">{service.vehicle.vehicle_type}</p>
                       </div>
                    </div>
                 )}

                 <div className="pt-6 border-t border-slate-50 flex items-center justify-between">
                    <div className="flex items-center gap-2 text-indigo-600 font-bold text-xs uppercase tracking-widest">
                       <FiShield /> Intención: {service?.governance_intention_id || 'VALIDANDO'}
                    </div>
                    <div className="text-right">
                       <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Total Pagado</p>
                       <p className="text-2xl font-black text-slate-900">${service?.estimated_price} COP</p>
                    </div>
                 </div>
              </div>
           </div>
        </ViewState>
      </div>
    </div>
  );
}

export default function DeliveryStatusPage() {
  return (
    <Suspense fallback={<div className="p-20 text-center">Cargando infraestructura logidstica...</div>}>
      <DeliveryStatusContent />
    </Suspense>
  );
}
