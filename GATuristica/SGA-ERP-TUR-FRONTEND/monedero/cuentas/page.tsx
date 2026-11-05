'use client';

import React from 'react';
import { FiPlus, FiMoreVertical, FiLock, FiUnlock, FiActivity } from 'react-icons/fi';

const wallets = [
  { id: 'W-9021', name: 'Monedero Principal', type: 'CORPORATE', balance: '$15,200,000', status: 'ACTIVE' },
  { id: 'W-4432', name: 'Reserva Comisiones', type: 'PROVIDER', balance: '$4,500,000', status: 'ACTIVE' },
  { id: 'W-8812', name: 'Fondo de Garantías', type: 'INTERNAL', balance: '$2,100,000', status: 'FROZEN' },
  { id: 'W-1123', name: 'Caja Menor Digital', type: 'EMPLOYEE', balance: '$450,000', status: 'ACTIVE' },
];

export default function CuentasPage() {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-black text-slate-900 dark:text-white uppercase tracking-tight">Gestión de Cuentas</h2>
          <p className="text-xs text-slate-500 font-medium">Administra los diferentes silos de saldo digital.</p>
        </div>
        <button className="flex items-center gap-2 px-6 py-3 bg-brand text-white rounded-2xl text-xs font-black uppercase tracking-widest shadow-lg shadow-brand/20 hover:scale-105 transition-all">
          <FiPlus /> Nueva Cuenta
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {wallets.map((wallet, i) => (
          <div key={i} className="bg-white dark:bg-black p-8 rounded-[40px] border border-slate-100 dark:border-white/5 group hover:border-brand/30 transition-all shadow-sm">
            <div className="flex items-start justify-between mb-6">
              <div className="space-y-1">
                <span className={`text-[8px] font-black px-2 py-1 rounded-md uppercase tracking-widest ${
                  wallet.type === 'CORPORATE' ? 'bg-indigo-500/10 text-indigo-500' : 'bg-slate-500/10 text-slate-500'
                }`}>
                  {wallet.type}
                </span>
                <h3 className="text-xl font-black text-slate-900 dark:text-white tracking-tight">{wallet.name}</h3>
                <p className="text-[10px] font-mono text-slate-400 uppercase">{wallet.id}</p>
              </div>
              <button className="p-2 hover:bg-slate-50 dark:hover:bg-white/5 rounded-xl transition-colors">
                <FiMoreVertical size={16} className="text-slate-400" />
              </button>
            </div>

            <div className="flex items-end justify-between">
              <div>
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Saldo Disponible</p>
                <p className="text-3xl font-black text-slate-900 dark:text-white tracking-tighter">{wallet.balance}</p>
              </div>

              <div className="flex gap-2">
                <button className="p-3 bg-slate-50 dark:bg-white/5 text-slate-400 hover:text-brand rounded-2xl transition-all">
                  <FiActivity size={18} />
                </button>
                {wallet.status === 'FROZEN' ? (
                  <button className="p-3 bg-rose-500/10 text-rose-500 rounded-2xl transition-all">
                    <FiLock size={18} />
                  </button>
                ) : (
                  <button className="p-3 bg-slate-50 dark:bg-white/5 text-slate-400 hover:text-emerald-500 rounded-2xl transition-all">
                    <FiUnlock size={18} />
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Sección de Auditoría de Cuentas */}
      <div className="bg-slate-900 rounded-[50px] p-10 text-white relative overflow-hidden">
        <div className="absolute right-0 top-0 w-1/2 h-full opacity-10 pointer-events-none">
          <FiShield size={400} className="translate-x-1/4 -translate-y-1/4" />
        </div>

        <div className="relative z-10 space-y-6 max-w-xl">
          <h2 className="text-3xl font-black tracking-tighter uppercase leading-none">Control de Integridad de Cartera</h2>
          <p className="text-slate-400 text-sm font-medium leading-relaxed">
            El sistema realiza conciliaciones automáticas cada 60 minutos comparando el balance acumulado con la suma de todos los hashes en el Ledger.
          </p>
          <div className="flex gap-4 pt-4">
            <button className="px-8 py-4 bg-white text-slate-900 rounded-2xl text-xs font-black uppercase tracking-widest hover:bg-brand hover:text-white transition-all">
              Ejecutar Conciliación Manual
            </button>
            <button className="px-8 py-4 bg-white/10 text-white border border-white/20 rounded-2xl text-xs font-black uppercase tracking-widest hover:bg-white/20 transition-all">
              Descargar Logs Ledger
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
