'use client';

import React, { useState } from 'react';
import { FiSend, FiSearch, FiUser, FiZap, FiCheckCircle } from 'react-icons/fi';

export default function TransferenciasPage() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

  const handleTransfer = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setStep(3);
    }, 2000);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="bg-white dark:bg-black p-8 md:p-12 rounded-[50px] border border-slate-100 dark:border-white/5 shadow-2xl">
        {step === 1 && (
          <div className="space-y-8 animate-in fade-in zoom-in duration-500">
            <div className="text-center space-y-2">
              <div className="w-16 h-16 bg-brand/10 text-brand rounded-3xl flex items-center justify-center mx-auto mb-4">
                <FiSend size={32} />
              </div>
              <h2 className="text-3xl font-black tracking-tight text-slate-900 dark:text-white uppercase">Transferencia Interna</h2>
              <p className="text-slate-500 text-sm font-medium">Envía fondos instantáneamente a cualquier usuario de SARITA.</p>
            </div>

            <div className="space-y-6">
              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-4">Destinatario (Email o ID)</label>
                <div className="relative group">
                  <FiSearch className="absolute left-6 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-brand transition-colors" />
                  <input
                    type="text"
                    placeholder="email@ejemplo.com"
                    className="w-full pl-14 pr-8 py-5 bg-slate-50 dark:bg-white/5 rounded-3xl border-none text-sm font-bold focus:ring-2 focus:ring-brand transition-all outline-none"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-4">Monto a Enviar (COP)</label>
                <input
                  type="number"
                  placeholder="0.00"
                  className="w-full px-8 py-8 bg-slate-50 dark:bg-white/5 rounded-[32px] border-none text-4xl font-black focus:ring-2 focus:ring-brand transition-all outline-none text-center"
                />
              </div>

              <button
                onClick={() => setStep(2)}
                className="w-full py-5 bg-brand text-white rounded-3xl font-black uppercase tracking-widest shadow-xl shadow-brand/20 hover:scale-[1.02] active:scale-95 transition-all"
              >
                Continuar
              </button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-8 animate-in slide-in-from-right duration-500">
            <h2 className="text-2xl font-black tracking-tight text-slate-900 dark:text-white uppercase text-center">Confirmar Transacción</h2>

            <div className="bg-slate-50 dark:bg-white/5 p-8 rounded-[40px] space-y-6">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Destino</span>
                <span className="text-sm font-black text-slate-900 dark:text-white">Juan Pérez (juan@perez.com)</span>
              </div>
              <div className="flex items-center justify-between border-t border-slate-200 dark:border-white/10 pt-6">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Monto</span>
                <span className="text-2xl font-black text-brand">$1,500,000</span>
              </div>
              <div className="flex items-center justify-between border-t border-slate-200 dark:border-white/10 pt-6">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Protocolo</span>
                <span className="text-[10px] font-black bg-emerald-500/10 text-emerald-500 px-3 py-1 rounded-full uppercase tracking-widest">Atómico e Idempotente</span>
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => setStep(1)}
                className="flex-1 py-5 bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-slate-400 rounded-3xl font-black uppercase tracking-widest hover:bg-slate-200 transition-all"
              >
                Atrás
              </button>
              <button
                onClick={handleTransfer}
                disabled={loading}
                className="flex-[2] py-5 bg-brand text-white rounded-3xl font-black uppercase tracking-widest shadow-xl shadow-brand/20 hover:scale-[1.02] active:scale-95 transition-all flex items-center justify-center gap-3"
              >
                {loading ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div> : <FiZap />}
                {loading ? 'Procesando...' : 'Confirmar y Enviar'}
              </button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="text-center space-y-8 animate-in zoom-in duration-500">
            <div className="w-24 h-24 bg-emerald-500 text-white rounded-[40px] flex items-center justify-center mx-auto shadow-2xl shadow-emerald-500/20">
              <FiCheckCircle size={48} />
            </div>
            <div className="space-y-2">
              <h2 className="text-3xl font-black tracking-tight text-slate-900 dark:text-white uppercase">¡Transferencia Exitosa!</h2>
              <p className="text-slate-500 text-sm font-medium">Los fondos han sido acreditados instantáneamente.</p>
            </div>

            <div className="bg-slate-50 dark:bg-white/5 p-6 rounded-3xl font-mono text-[10px] text-slate-500 break-all leading-relaxed max-w-sm mx-auto">
              HASH INTEGRIDAD: <br/>
              <span className="text-brand font-black">7a89bc2d4e1f56a7d890c1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2</span>
            </div>

            <button
              onClick={() => setStep(1)}
              className="w-full py-5 border-2 border-slate-100 dark:border-white/10 text-slate-900 dark:text-white rounded-3xl font-black uppercase tracking-widest hover:bg-slate-50 dark:hover:bg-white/5 transition-all"
            >
              Nueva Transferencia
            </button>
          </div>
        )}
      </div>

      {/* Recientes */}
      <div className="bg-white dark:bg-black p-8 rounded-[40px] border border-slate-100 dark:border-white/5">
        <h3 className="text-xs font-black text-slate-400 uppercase tracking-[0.2em] mb-6">Contactos Recientes</h3>
        <div className="flex gap-4 overflow-x-auto pb-2 scrollbar-hide">
          {[
            { name: 'Maria C.', img: 'MC' },
            { name: 'Carlos R.', img: 'CR' },
            { name: 'Sede Central', img: 'SC' },
            { name: 'Logística', img: 'LG' },
            { name: 'Juan P.', img: 'JP' },
          ].map((contact, i) => (
            <div key={i} className="flex flex-col items-center gap-2 cursor-pointer group min-w-[80px]">
              <div className="w-14 h-14 rounded-2xl bg-slate-100 dark:bg-white/5 flex items-center justify-center text-sm font-black text-slate-500 group-hover:bg-brand group-hover:text-white transition-all">
                {contact.img}
              </div>
              <span className="text-[10px] font-bold text-slate-500 truncate w-full text-center">{contact.name}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
