'use client';

import React, { useEffect, useState } from 'react';
import api from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { FiGift, FiSearch, FiTrendingUp, FiCreditCard } from 'react-icons/fi';
import { ViewState } from '@/components/ui/ViewState';

export default function GiftAuditPage() {
  const [gifts, setGifts] = useState<any[]>([]);
  const [audit, setAudit] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [giftsRes, auditRes] = await Promise.all([
          api.get('/admin/plataforma/system-audit/financial/gift-catalog/'),
          api.get('/admin/plataforma/system-audit/financial/gift-audit/')
      ]);
      setGifts(giftsRes.data);
      setAudit(auditRes.data);
    } catch (e) {
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      <div className="flex justify-between items-end">
        <div>
           <div className="flex items-center gap-2 text-pink-600 font-bold mb-2 uppercase tracking-widest text-xs">
              <FiGift /> Auditoría Económica Vía 3
           </div>
           <h1 className="text-5xl font-black text-slate-900 tracking-tighter uppercase">Motor de Premios y Regalos</h1>
           <p className="text-slate-500 font-medium mt-1">Supervisión de transacciones sociales y recaudo de comisiones del 2%.</p>
        </div>
      </div>

      <ViewState isLoading={isLoading}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* AUDIT LOG */}
            <div className="lg:col-span-2">
                <Card className="border-none shadow-xl bg-white rounded-[2.5rem] overflow-hidden">
                    <CardHeader className="p-8 border-b border-slate-50">
                        <CardTitle className="text-xl font-black uppercase tracking-tight">Historial Reciente de Regalos</CardTitle>
                    </CardHeader>
                    <CardContent className="p-0">
                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead className="bg-slate-50 text-[10px] font-black text-slate-400 uppercase tracking-widest">
                                    <tr>
                                        <th className="px-8 py-4">Emisor</th>
                                        <th className="px-8 py-4">Receptor</th>
                                        <th className="px-8 py-4">Monto</th>
                                        <th className="px-8 py-4 text-pink-600">Comisión (2%)</th>
                                        <th className="px-8 py-4">Estado</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-50">
                                    {audit.map((tx) => (
                                        <tr key={tx.id} className="hover:bg-slate-50/50 transition-colors">
                                            <td className="px-8 py-6 font-bold text-sm text-slate-700">{tx.sender}</td>
                                            <td className="px-8 py-6 font-bold text-sm text-slate-700">{tx.receiver}</td>
                                            <td className="px-8 py-6 font-black text-sm text-slate-900">${tx.amount}</td>
                                            <td className="px-8 py-6 font-black text-sm text-pink-600">+${tx.commission_2pct}</td>
                                            <td className="px-8 py-6">
                                                <Badge className="bg-emerald-100 text-emerald-700 text-[9px] font-black uppercase">{tx.status}</Badge>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* CATALOG SUMMARY */}
            <div className="space-y-8">
                <Card className="border-none shadow-xl bg-slate-900 text-white p-10 rounded-[2.5rem]">
                   <p className="text-xs font-black uppercase tracking-[0.2em] text-pink-400 mb-4">Recaudo Estimado Comisiones</p>
                   <h3 className="text-6xl font-black italic tracking-tighter">
                       ${audit.reduce((acc, curr) => acc + curr.commission_2pct, 0).toLocaleString()}
                   </h3>
                   <p className="text-[10px] text-slate-500 mt-6 uppercase font-bold tracking-widest">Fondos dirigidos a la Wallet Corporativa</p>
                </Card>

                <h3 className="text-xl font-black text-slate-900 uppercase tracking-widest flex items-center gap-2 italic">
                    <FiSearch className="text-indigo-500" /> Catálogo Activo
                </h3>
                <div className="grid grid-cols-1 gap-4 max-h-[500px] overflow-y-auto pr-2">
                    {gifts.map((gift) => (
                        <div key={gift.id} className="bg-white p-6 rounded-2xl shadow-sm flex justify-between items-center border border-slate-100">
                            <div>
                                <h4 className="font-bold text-slate-900">{gift.name}</h4>
                                <p className="text-xs text-slate-400">Código: {gift.code}</p>
                            </div>
                            <div className="text-right">
                                <p className="font-black text-indigo-600">${gift.price}</p>
                                <Badge className="bg-slate-100 text-slate-500 text-[8px] uppercase">ACTIVO</Badge>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
      </ViewState>
    </div>
  );
}
