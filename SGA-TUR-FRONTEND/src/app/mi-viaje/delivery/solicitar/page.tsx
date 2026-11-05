"use client";

import React, { useState, useEffect } from 'react';
import api from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { FiTruck, FiMapPin, FiPackage, FiArrowRight, FiShield } from 'react-icons/fi';
import { useRouter } from 'next/navigation';
import { toast } from 'react-toastify';

export default function SolicitarDeliveryPage() {
  const { token, user } = useAuth();
  const router = useRouter();

  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [vehicleType, setVehicleType] = useState('MOTO');
  const [companies, setCompanies] = useState<any[]>([]);
  const [selectedCompany, setSelectedCompany] = useState('');
  const [estimatedPrice, setEstimatedPrice] = useState(15000);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const fetchCompanies = async () => {
      try {
        const res = await api.get('/delivery/companies/');
        setCompanies(res.data.results || []);
      } catch (err) {
        console.error("Error fetching delivery companies", err);
      }
    };
    fetchCompanies();
  }, []);

  const handleRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!origin || !destination) return;

    setIsSubmitting(true);
    try {
      const response = await api.post('/delivery/services/request_delivery/', {
        origin_address: origin,
        destination_address: destination,
        vehicle_type: vehicleType,
        delivery_company: selectedCompany || null,
        estimated_price: estimatedPrice
      });

      if (response.data.status === 'SUCCESS') {
        toast.success("Solicitud registrada bajo gobernanza SARITA.");
        router.push(`/mi-viaje/delivery/estado?id=${response.data.service_id}`);
      }
    } catch (err: any) {
      toast.error(err.response?.data?.error || "Error al solicitar delivery.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-[2.5rem] p-10 shadow-xl border border-slate-100">
           <div className="flex items-center gap-4 mb-10">
              <div className="w-16 h-16 bg-indigo-600 text-white rounded-2xl flex items-center justify-center shadow-lg shadow-indigo-100">
                 <FiTruck size={32} />
              </div>
              <div>
                 <h1 className="text-3xl font-black text-slate-900 tracking-tight">Solicitar Delivery / Transporte</h1>
                 <p className="text-slate-500 font-medium">Logística Institucional Certificada.</p>
              </div>
           </div>

           <form onSubmit={handleRequest} className="space-y-8">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                 <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-4">Punto de Recogida (Origen)</label>
                    <div className="relative">
                       <FiMapPin className="absolute left-6 top-5 text-indigo-500" />
                       <input
                          type="text"
                          required
                          value={origin}
                          onChange={(e) => setOrigin(e.target.value)}
                          placeholder="Ej: Hotel Central"
                          className="w-full pl-14 pr-6 py-4 bg-slate-50 border-none rounded-2xl font-bold focus:ring-2 focus:ring-indigo-500 transition-all"
                       />
                    </div>
                 </div>

                 <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-4">Destino Final</label>
                    <div className="relative">
                       <FiMapPin className="absolute left-6 top-5 text-red-500" />
                       <input
                          type="text"
                          required
                          value={destination}
                          onChange={(e) => setDestination(e.target.value)}
                          placeholder="Ej: Atractivo Río Gaitán"
                          className="w-full pl-14 pr-6 py-4 bg-slate-50 border-none rounded-2xl font-bold focus:ring-2 focus:ring-indigo-500 transition-all"
                       />
                    </div>
                 </div>
              </div>

              <div className="space-y-4">
                 <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-4">Empresa (Opcional)</label>
                 <select
                    value={selectedCompany}
                    onChange={(e) => setSelectedCompany(e.target.value)}
                    className="w-full px-6 py-4 bg-slate-50 border-none rounded-2xl font-bold focus:ring-2 focus:ring-indigo-500 transition-all appearance-none"
                 >
                    <option value="">Cualquier empresa disponible</option>
                    {companies.map(c => (
                       <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                 </select>
              </div>

              <div className="space-y-4">
                 <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-4">Tipo de Vehículo</label>
                 <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    {['MOTO', 'MOTOCARRO', 'AUTO', 'VAN'].map((type) => (
                       <button
                          key={type}
                          type="button"
                          onClick={() => setVehicleType(type)}
                          className={`py-4 rounded-2xl font-bold text-xs transition-all border-2 ${
                             vehicleType === type
                             ? 'bg-indigo-600 border-indigo-600 text-white shadow-lg'
                             : 'bg-white border-slate-100 text-slate-500 hover:border-indigo-200'
                          }`}
                       >
                          {type}
                       </button>
                    ))}
                 </div>
              </div>

              <div className="bg-indigo-50 p-8 rounded-[2rem] border border-indigo-100 flex items-center justify-between">
                 <div>
                    <p className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-1">Precio Estimado Gobernado</p>
                    <p className="text-3xl font-black text-indigo-900">${estimatedPrice.toLocaleString()} <span className="text-sm font-medium">COP</span></p>
                 </div>
                 <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center text-indigo-600">
                    <FiPackage size={24} />
                 </div>
              </div>

              <button
                 type="submit"
                 disabled={isSubmitting}
                 className="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-6 rounded-3xl font-black uppercase tracking-[0.2em] text-sm transition-all shadow-xl shadow-indigo-100 flex items-center justify-center gap-3"
              >
                 {isSubmitting ? 'Registrando Intención...' : (
                    <>
                       Confirmar y Solicitar Servicio <FiArrowRight />
                    </>
                 )}
              </button>

              <div className="flex items-center justify-center gap-2 text-[10px] font-black text-slate-400 uppercase tracking-tighter">
                 <FiShield /> Servicio Garantizado por la Soberanía SARITA
              </div>
           </form>
        </div>
      </div>
    </div>
  );
}
