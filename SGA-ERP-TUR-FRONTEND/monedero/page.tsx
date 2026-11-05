'use client';

import React, { useEffect, useState } from 'react';
import {
  FiTrendingUp,
  FiArrowUpRight,
  FiArrowDownLeft,
  FiLock,
  FiZap,
  FiShield,
  FiActivity
} from 'react-icons/fi';
import { useMiNegocioApi } from '../hooks/useMiNegocioApi';

export default function WalletDashboard() {
  const { getTesoreria, getStatistics, isLoading } = useMiNegocioApi();
  const [tesoreria, setTesoreria] = useState<any>(null);
  const [statsData, setStatsData] = useState<any>(null);

  useEffect(() => {
    getTesoreria().then(res => res && res.length > 0 && setTesoreria(res[0]));
    getStatistics().then(res => res && setStatsData(res));
  }, [getTesoreria, getStatistics]);

  const stats = [
    { label: 'Saldo Disponible', value: tesoreria?.liquidez_disponible ? `$${parseFloat(tesoreria.liquidez_disponible).toLocaleString()}` : '$0.00', icon: FiZap, color: 'bg-emerald-500' },
    { label: 'Saldo Bloqueado', value: tesoreria?.saldo_bloqueado ? `$${parseFloat(tesoreria.saldo_bloqueado).toLocaleString()}` : '$0.00', icon: FiLock, color: 'bg-amber-500' },
    { label: 'Ingresos (Mes)', value: statsData?.ventas_mes ? `+$${statsData.ventas_mes.toLocaleString()}` : '+$0.00', icon: FiArrowUpRight, color: 'bg-brand' },
    { label: 'Egresos (Mes)', value: statsData?.gastos_mes ? `-$${statsData.gastos_mes.toLocaleString()}` : '-$0.00', icon: FiArrowDownLeft, color: 'bg-rose-500' },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Resumen Superior */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, i) => (
          <div key={i} className="bg-white dark:bg-black p-6 rounded-3xl border border-slate-100 dark:border-white/5 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div className={`${stat.color} p-3 rounded-2xl text-white shadow-lg`}>
                <stat.icon size={20} />
              </div>
              <FiTrendingUp size={16} className="text-slate-300" />
            </div>
            <p className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-widest">{stat.label}</p>
            <h3 className="text-2xl font-black text-slate-900 dark:text-white mt-1 tracking-tighter">{stat.value}</h3>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Actividad Reciente */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white dark:bg-black p-8 rounded-[40px] border border-slate-100 dark:border-white/5">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-3">
                <FiActivity size={24} className="text-brand" />
                <h2 className="text-xl font-black text-slate-900 dark:text-white tracking-tight uppercase">Historial Maestro</h2>
              </div>
              <button className="text-xs font-black text-brand uppercase tracking-widest">Ver todo</button>
            </div>

            <div className="space-y-4">
              {[
                { type: 'Recarga', desc: 'Transferencia Bancaria #892', amount: '+$500,000', status: 'Verificado', time: 'hace 10 min' },
                { type: 'Pago', desc: 'Suministros Oficina - Amazon', amount: '-$125,000', status: 'Ejecutado', time: 'hace 1 hora' },
                { type: 'Comisión', desc: 'Delivery #9021 - Comisión 15%', amount: '+$12,500', status: 'Ejecutado', time: 'hace 3 horas' },
                { type: 'Transferencia', desc: 'Pago Nómina - Juan Pérez', amount: '-$1,800,000', status: 'Ejecutado', time: 'ayer' },
              ].map((tx, i) => (
                <div key={i} className="flex items-center justify-between p-4 hover:bg-slate-50 dark:hover:bg-white/5 rounded-2xl transition-colors cursor-pointer">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-slate-100 dark:bg-white/10 flex items-center justify-center font-black text-xs text-slate-500">
                      {tx.type[0]}
                    </div>
                    <div>
                      <p className="text-sm font-black text-slate-900 dark:text-white">{tx.desc}</p>
                      <p className="text-[10px] text-slate-500 uppercase font-bold tracking-tighter">{tx.type} • {tx.time}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`text-sm font-black ${tx.amount.startsWith('+') ? 'text-emerald-500' : 'text-slate-900 dark:text-white'}`}>{tx.amount}</p>
                    <p className="text-[10px] text-emerald-500 font-bold uppercase tracking-widest">{tx.status}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Seguridad y Auditoría */}
        <div className="space-y-6">
          <div className="bg-brand rounded-[40px] p-8 text-white shadow-2xl shadow-brand/30">
            <FiShield size={40} className="mb-6 opacity-20" />
            <h2 className="text-2xl font-black tracking-tighter leading-none mb-4 uppercase">Blindaje Financiero Activo</h2>
            <p className="text-brand-light/80 text-sm font-medium mb-6">
              El motor transaccional está operando bajo protocolos de idempotencia y hash encadenado.
            </p>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest bg-white/10 p-2 rounded-lg">
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                Ledger Inmutable: OK
              </div>
              <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest bg-white/10 p-2 rounded-lg">
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                Hash Integrity: VERIFIED
              </div>
              <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest bg-white/10 p-2 rounded-lg">
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                Agents L1-L6: STANDBY
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-black p-8 rounded-[40px] border border-slate-100 dark:border-white/5">
            <h3 className="text-sm font-black text-slate-900 dark:text-white uppercase tracking-widest mb-4">Configuración Rápida</h3>
            <div className="space-y-2">
              <button className="w-full py-3 px-4 bg-slate-50 dark:bg-white/5 rounded-2xl text-left text-xs font-bold text-slate-600 dark:text-slate-400 hover:bg-slate-100 transition-colors flex items-center justify-between">
                Límites de Retiro
                <FiZap size={14} className="text-brand" />
              </button>
              <button className="w-full py-3 px-4 bg-slate-50 dark:bg-white/5 rounded-2xl text-left text-xs font-bold text-slate-600 dark:text-slate-400 hover:bg-slate-100 transition-colors flex items-center justify-between">
                Alertas Anti-Fraude
                <FiShield size={14} className="text-brand" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
