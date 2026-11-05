"use client";

import React, { useState, useEffect, useCallback } from 'react';
import api from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { FiShield, FiDollarSign, FiActivity, FiLock, FiClock } from 'react-icons/fi';
import { ViewState } from '@/components/ui/ViewState';
import Link from 'next/link';

export default function WalletCarteraPage() {
  const { token, user } = useAuth();
  const [wallet, setWallet] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchWallet = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const response = await api.get('/wallet/accounts/');
      if (response.data.results && response.data.results.length > 0) {
        setWallet(response.data.results[0]);
      } else {
        setError("No se encontró una cartera activa para su usuario.");
      }
    } catch (err) {
      setError("Error al cargar la información de la cartera.");
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchWallet();
  }, [fetchWallet]);

  return (
    <div className="min-h-screen bg-slate-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="flex items-center justify-between">
           <div>
              <h1 className="text-3xl font-black text-slate-900 tracking-tight">Mi Cartera Soberana</h1>
              <p className="text-slate-500 font-medium">Custodia institucional de activos digitales.</p>
           </div>
           <div className="bg-indigo-100 text-indigo-700 px-4 py-2 rounded-2xl text-xs font-black uppercase tracking-widest flex items-center gap-2">
              <FiShield /> Estatus: {wallet?.status || 'VALIDANDO'}
           </div>
        </div>

        <ViewState isLoading={isLoading} error={error}>
           <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Tarjeta de Saldo Principal */}
              <div className="bg-white rounded-[2.5rem] p-10 shadow-2xl shadow-indigo-100 border border-slate-100 relative overflow-hidden group">
                 <div className="absolute top-0 right-0 p-8 text-slate-50 opacity-10 group-hover:scale-110 transition-transform duration-700">
                    <FiDollarSign size={120} />
                 </div>
                 <div className="relative z-10">
                    <p className="text-slate-400 font-black uppercase tracking-widest text-xs mb-4">Saldo Disponible</p>
                    <h2 className="text-6xl font-black text-slate-900 mb-2">${wallet?.balance || '0.00'} <span className="text-xl text-slate-400 font-medium">COP</span></h2>

                    {wallet?.locked_balance > 0 && (
                      <div className="flex items-center gap-2 text-amber-600 mb-8 font-bold text-sm bg-amber-50 w-fit px-3 py-1 rounded-full border border-amber-100">
                        <FiLock size={14} />
                        ${wallet.locked_balance} Bloqueados por servicios activos
                      </div>
                    )}

                    <div className="flex gap-4 mt-8">
                       <Link href="/mi-viaje/monedero/transferir" className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white py-4 rounded-2xl font-bold text-center transition-all shadow-lg shadow-indigo-200">
                          Transferir
                       </Link>
                       <button className="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 py-4 rounded-2xl font-bold transition-all">
                          Cargar
                       </button>
                    </div>
                 </div>
              </div>

              {/* Información de Cuenta */}
              <div className="space-y-6">
                 <div className="bg-white rounded-3xl p-6 border border-slate-100 shadow-sm flex items-center gap-4">
                    <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center">
                       <FiActivity size={24} />
                    </div>
                    <div>
                       <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">ID de Cartera</p>
                       <p className="font-mono text-xs font-bold text-slate-900 truncate w-48">{wallet?.id}</p>
                    </div>
                 </div>

                 <div className="bg-white rounded-3xl p-6 border border-slate-100 shadow-sm flex items-center gap-4">
                    <div className="w-12 h-12 bg-green-100 text-green-600 rounded-2xl flex items-center justify-center">
                       <FiLock size={24} />
                    </div>
                    <div>
                       <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Nivel de Seguridad</p>
                       <p className="font-bold text-slate-900">Institucional SARITA</p>
                    </div>
                 </div>

                 <div className="bg-white rounded-3xl p-6 border border-slate-100 shadow-sm flex items-center gap-4">
                    <div className="w-12 h-12 bg-amber-100 text-amber-600 rounded-2xl flex items-center justify-center">
                       <FiClock size={24} />
                    </div>
                    <div>
                       <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Última Actividad</p>
                       <p className="font-bold text-slate-900">{wallet ? new Date(wallet.updated_at).toLocaleDateString() : 'N/A'}</p>
                    </div>
                 </div>
              </div>
           </div>

           <div className="mt-12">
              <Link href="/mi-viaje/monedero/transacciones" className="text-indigo-600 font-bold hover:underline flex items-center gap-2">
                 Ver historial completo de transacciones →
              </Link>
           </div>
        </ViewState>
      </div>
    </div>
  );
}
