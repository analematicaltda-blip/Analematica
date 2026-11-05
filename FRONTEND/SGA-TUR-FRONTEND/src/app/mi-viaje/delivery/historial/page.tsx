"use client";

import React, { useState, useEffect, useCallback } from 'react';
import api from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { FiList, FiArrowLeft, FiMapPin, FiCalendar, FiArrowRight, FiStar } from 'react-icons/fi';
import { toast } from 'react-toastify';
import { useRouter } from 'next/navigation';
import { ViewState } from '@/components/ui/ViewState';
import Link from 'next/link';

export default function DeliveryHistorialPage() {
  const { token } = useAuth();
  const router = useRouter();
  const [services, setServices] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = useCallback(async () => {
    if (!token) return;
    try {
      const response = await api.get('/delivery/services/');
      setServices(response.data.results || []);
    } catch (err) {
      setError("Error al cargar el historial de logística.");
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const handleRate = async (id: string, rating: number) => {
    try {
      await api.post(`/delivery/services/${id}/rate/`, { rating });
      toast.success("Gracias por su calificación soberana.");
      fetchHistory();
    } catch (err) {
      toast.error("Error al calificar el servicio.");
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 py-12 px-4">
      <div className="max-w-5xl mx-auto space-y-8">
        <button onClick={() => router.back()} className="text-slate-500 hover:text-slate-900 flex items-center gap-2 font-bold transition-colors">
           <FiArrowLeft /> Regresar
        </button>

        <div className="flex items-center gap-4">
           <div className="w-16 h-16 bg-white border border-slate-100 rounded-2xl flex items-center justify-center shadow-sm">
              <FiList size={32} className="text-indigo-600" />
           </div>
           <div>
              <h1 className="text-3xl font-black text-slate-900 tracking-tight">Historial de Logística</h1>
              <p className="text-slate-500 font-medium">Todos sus traslados y entregas institucionales.</p>
           </div>
        </div>

        <ViewState isLoading={isLoading} error={error} isEmpty={services.length === 0}>
           <div className="grid grid-cols-1 gap-6">
              {services.map((item: any) => (
                 <div key={item.id} className="bg-white p-8 rounded-[2.5rem] shadow-md border border-slate-50 hover:shadow-xl transition-all group">
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                       <div className="flex-1 space-y-4">
                          <div className="flex items-center gap-3">
                             <span className={`text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-widest ${
                                item.status === 'COMPLETED' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'
                             }`}>
                                {item.status}
                             </span>
                             <p className="text-xs text-slate-400 flex items-center gap-1 font-bold">
                                <FiCalendar /> {new Date(item.created_at).toLocaleDateString()}
                             </p>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                             <div className="flex items-start gap-3">
                                <FiMapPin className="mt-1 text-indigo-500" />
                                <div>
                                   <p className="text-[9px] font-black text-slate-400 uppercase">Origen</p>
                                   <p className="text-sm font-bold text-slate-900">{item.origin_address}</p>
                                </div>
                             </div>
                             <div className="flex items-start gap-3">
                                <FiMapPin className="mt-1 text-red-500" />
                                <div>
                                   <p className="text-[9px] font-black text-slate-400 uppercase">Destino</p>
                                   <p className="text-sm font-bold text-slate-900">{item.destination_address}</p>
                                </div>
                             </div>
                          </div>
                       </div>

                       <div className="w-full md:w-auto text-right flex flex-col gap-4">
                          <div>
                             <p className="text-[10px] font-black text-slate-400 uppercase">Costo del Servicio</p>
                             <p className="text-2xl font-black text-slate-900">${item.estimated_price} COP</p>
                          </div>
                          {item.status === 'COMPLETED' && !item.rating && (
                            <div className="flex items-center justify-end gap-1">
                               {[1, 2, 3, 4, 5].map((star) => (
                                 <button
                                   key={star}
                                   onClick={() => handleRate(item.id, star)}
                                   className="text-slate-300 hover:text-amber-400 transition-colors"
                                 >
                                   <FiStar />
                                 </button>
                               ))}
                            </div>
                          )}

                          {item.rating && (
                            <div className="flex items-center justify-end gap-1 text-amber-500 font-bold text-xs uppercase tracking-widest">
                               {item.rating} <FiStar fill="currentColor" />
                            </div>
                          )}

                          <Link
                             href={`/mi-viaje/delivery/estado?id=${item.id}`}
                             className="bg-slate-900 text-white px-6 py-3 rounded-2xl text-xs font-black uppercase tracking-widest flex items-center justify-center gap-2 hover:bg-slate-800 transition-colors"
                          >
                             Ver Detalle <FiArrowRight />
                          </Link>
                       </div>
                    </div>
                 </div>
              ))}
           </div>
        </ViewState>
      </div>
    </div>
  );
}
