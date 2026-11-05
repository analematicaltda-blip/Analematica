"use client";

import React, { useState, useEffect, useCallback } from 'react';
import api from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { FiSend, FiArrowLeft, FiAlertCircle, FiCheckCircle } from 'react-icons/fi';
import { useRouter } from 'next/navigation';

export default function WalletTransferirPage() {
  const { token, user } = useAuth();
  const router = useRouter();

  const [amount, setAmount] = useState('');
  const [recipientId, setRecipientId] = useState('');
  const [description, setDescription] = useState('');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [status, setStatus] = useState<'IDLE' | 'PENDING' | 'SUCCESS' | 'ERROR'>('IDLE');
  const [message, setMessage] = useState('');
  const [wallet, setWallet] = useState<any>(null);

  useEffect(() => {
    const fetchWallet = async () => {
      try {
        const res = await api.get('/wallet/accounts/');
        if (res.data.results.length > 0) setWallet(res.data.results[0]);
      } catch (err) {}
    };
    fetchWallet();
  }, []);

  const handleTransfer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!amount || !recipientId) return;

    setIsSubmitting(true);
    setStatus('PENDING');
    setMessage("Registrando Intención Financiera en el Kernel...");

    try {
      // Flujo: Intención -> Kernel -> Ejecución
      const response = await api.post('/wallet/accounts/pay/', {
        to_wallet_id: recipientId,
        amount: parseFloat(amount),
        description: description || "Transferencia entre usuarios"
      });

      if (response.data.status === 'SUCCESS') {
        setStatus('SUCCESS');
        setMessage(`Transferencia exitosa. ID: ${response.data.transaction_id}`);
        setTimeout(() => router.push('/mi-viaje/monedero/cartera'), 3000);
      } else {
        throw new Error(response.data.message || "Error en la ejecución soberana.");
      }
    } catch (err: any) {
      setStatus('ERROR');
      setMessage(err.response?.data?.error || err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-xl mx-auto">
        <button onClick={() => router.back()} className="mb-8 text-slate-500 hover:text-slate-900 flex items-center gap-2 font-bold transition-colors">
           <FiArrowLeft /> Regresar
        </button>

        <div className="bg-white rounded-[2.5rem] p-10 shadow-xl border border-slate-100">
           <div className="flex items-center gap-4 mb-8">
              <div className="w-14 h-14 bg-indigo-600 text-white rounded-2xl flex items-center justify-center shadow-lg shadow-indigo-100">
                 <FiSend size={28} />
              </div>
              <div>
                 <h1 className="text-2xl font-black text-slate-900">Transferir Fondos</h1>
                 <p className="text-slate-500 font-medium text-sm">Operación gobernada por el Kernel.</p>
              </div>
           </div>

           {status === 'SUCCESS' ? (
              <div className="text-center py-10 space-y-6">
                 <div className="w-20 h-20 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto">
                    <FiCheckCircle size={40} />
                 </div>
                 <h2 className="text-2xl font-black text-slate-900">¡Acción Validada!</h2>
                 <p className="text-slate-500">{message}</p>
                 <button onClick={() => router.push('/mi-viaje/monedero/cartera')} className="w-full bg-slate-900 text-white py-4 rounded-2xl font-bold">
                    Ir a mi Cartera
                 </button>
              </div>
           ) : (
              <form onSubmit={handleTransfer} className="space-y-6">
                 <div className="bg-slate-50 p-6 rounded-3xl border border-slate-100 mb-8">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Mi Saldo Actual</p>
                    <p className="text-2xl font-black text-slate-900">${wallet?.balance || '0.00'} COP</p>
                 </div>

                 <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-4">Monto a Transferir (COP)</label>
                    <input
                       type="number"
                       required
                       value={amount}
                       onChange={(e) => setAmount(e.target.value)}
                       placeholder="0.00"
                       className="w-full px-6 py-4 bg-slate-50 border-none rounded-2xl text-lg font-bold focus:ring-2 focus:ring-indigo-500 transition-all"
                    />
                 </div>

                 <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-4">ID del Destinatario (Wallet ID)</label>
                    <input
                       type="text"
                       required
                       value={recipientId}
                       onChange={(e) => setRecipientId(e.target.value)}
                       placeholder="UUID de la cartera destino"
                       className="w-full px-6 py-4 bg-slate-50 border-none rounded-2xl text-sm font-mono focus:ring-2 focus:ring-indigo-500 transition-all"
                    />
                 </div>

                 <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-4">Concepto / Motivo</label>
                    <textarea
                       value={description}
                       onChange={(e) => setDescription(e.target.value)}
                       placeholder="Ej: Pago de guía turístico..."
                       className="w-full px-6 py-4 bg-slate-50 border-none rounded-2xl text-sm focus:ring-2 focus:ring-indigo-500 transition-all h-24"
                    />
                 </div>

                 {status === 'ERROR' && (
                    <div className="bg-red-50 text-red-600 p-4 rounded-2xl flex items-center gap-3 text-sm font-bold border border-red-100">
                       <FiAlertCircle className="flex-shrink-0" />
                       {message}
                    </div>
                 )}

                 <button
                    type="submit"
                    disabled={isSubmitting || !amount || !recipientId}
                    className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-200 text-white py-5 rounded-[1.5rem] font-black uppercase tracking-widest text-xs transition-all shadow-xl shadow-indigo-100"
                 >
                    {isSubmitting ? 'Validando Intención...' : 'Confirmar e Iniciar Transferencia'}
                 </button>

                 <p className="text-[9px] text-center text-slate-400 font-bold uppercase tracking-tighter mt-4 px-8">
                    Toda transacción es final y queda registrada en la bitácora forense de SARITA bajo supervisión institucional.
                 </p>
              </form>
           )}
        </div>
      </div>
    </div>
  );
}
