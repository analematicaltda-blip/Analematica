"use client";

import React, { useState, useEffect, useCallback } from 'react';
import api from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { FiList, FiArrowLeft, FiShield, FiFileText } from 'react-icons/fi';
import { useRouter } from 'next/navigation';
import { ViewState } from '@/components/ui/ViewState';

export default function WalletTransaccionesPage() {
  const { token } = useAuth();
  const router = useRouter();
  const [transactions, setTransactions] = useState<any[]>([]);
  const [filteredTransactions, setFilteredTransactions] = useState<any[]>([]);
  const [filter, setFilter] = useState('ALL');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTransactions = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const response = await api.get('/wallet/transactions/');
      const data = response.data.results || [];
      setTransactions(data);
      setFilteredTransactions(data);
    } catch (err) {
      setError("Error al cargar el historial de transacciones.");
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  useEffect(() => {
    if (filter === 'ALL') {
      setFilteredTransactions(transactions);
    } else {
      setFilteredTransactions(transactions.filter(tx => tx.type === filter));
    }
  }, [filter, transactions]);

  return (
    <div className="min-h-screen bg-slate-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-8">
        <button onClick={() => router.back()} className="text-slate-500 hover:text-slate-900 flex items-center gap-2 font-bold transition-colors">
           <FiArrowLeft /> Regresar
        </button>

        <div className="flex items-center gap-4">
           <div className="w-16 h-16 bg-white border border-slate-100 rounded-2xl flex items-center justify-center shadow-sm">
              <FiList size={32} className="text-indigo-600" />
           </div>
           <div>
              <h1 className="text-3xl font-black text-slate-900 tracking-tight">Historial Financiero</h1>
              <p className="text-slate-500 font-medium">Registro forense de todas sus operaciones económicas.</p>
           </div>
        </div>

        <div className="flex gap-2 bg-white p-2 rounded-2xl border border-slate-100 shadow-sm w-fit">
           {['ALL', 'DEPOSIT', 'PAYMENT', 'REFUND'].map((f) => (
             <button
               key={f}
               onClick={() => setFilter(f)}
               className={`px-4 py-2 rounded-xl text-[10px] font-black tracking-widest transition-all ${
                 filter === f ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-100' : 'text-slate-400 hover:text-slate-600'
               }`}
             >
               {f}
             </button>
           ))}
        </div>

        <ViewState isLoading={isLoading} error={error} isEmpty={filteredTransactions.length === 0}>
           <div className="bg-white rounded-[2.5rem] shadow-xl border border-slate-100 overflow-hidden">
              <div className="overflow-x-auto">
                 <table className="w-full text-left">
                    <thead>
                       <tr className="bg-slate-50">
                          <th className="px-8 py-6 text-[10px] font-black uppercase tracking-widest text-slate-400">Fecha / Referencia</th>
                          <th className="px-8 py-6 text-[10px] font-black uppercase tracking-widest text-slate-400">Tipo</th>
                          <th className="px-8 py-6 text-[10px] font-black uppercase tracking-widest text-slate-400">Concepto</th>
                          <th className="px-8 py-6 text-[10px] font-black uppercase tracking-widest text-slate-400">ID Intención</th>
                          <th className="px-8 py-6 text-[10px] font-black uppercase tracking-widest text-slate-400 text-right">Monto</th>
                       </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                       {filteredTransactions.map((tx: any) => (
                          <tr key={tx.id} className="hover:bg-slate-50 transition-colors">
                             <td className="px-8 py-6">
                                <p className="text-sm font-bold text-slate-900">{new Date(tx.timestamp).toLocaleString()}</p>
                                <p className="text-[10px] font-mono text-slate-400 uppercase tracking-tighter truncate w-32">{tx.id}</p>
                             </td>
                             <td className="px-8 py-6">
                                <span className={`text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-widest ${
                                   tx.type === 'DEPOSIT' ? 'bg-green-100 text-green-700' :
                                   tx.type === 'PAYMENT' ? 'bg-indigo-100 text-indigo-700' :
                                   'bg-slate-100 text-slate-600'
                                }`}>
                                   {tx.type}
                                </span>
                             </td>
                             <td className="px-8 py-6">
                                <p className="text-sm font-medium text-slate-600">{tx.description || 'Sin concepto registrado'}</p>
                             </td>
                             <td className="px-8 py-6">
                                <div className="flex items-center gap-2 text-indigo-500">
                                   <FiShield size={14} />
                                   <p className="text-[10px] font-mono font-bold">{tx.governance_intention_id || 'SARITA-NATIVE'}</p>
                                </div>
                             </td>
                             <td className="px-8 py-6 text-right">
                                <p className={`text-lg font-black ${tx.type === 'DEPOSIT' ? 'text-green-600' : 'text-slate-900'}`}>
                                   {tx.type === 'DEPOSIT' ? '+' : '-'}${tx.amount}
                                </p>
                                <div className="flex items-center justify-end gap-1 text-green-600 font-bold text-[9px] uppercase tracking-widest">
                                   <FiFileText /> Auditado
                                </div>
                             </td>
                          </tr>
                       ))}
                    </tbody>
                 </table>
              </div>
           </div>
        </ViewState>
      </div>
    </div>
  );
}
