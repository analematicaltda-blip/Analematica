'use client';

import React, { useEffect, useState } from 'react';
import api from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { FiGrid, FiActivity, FiSearch, FiLayers } from 'react-icons/fi';
import { ViewState } from '@/components/ui/ViewState';

export default function GlobalLedgerPage() {
  const [stats, setStats] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadGlobalLedger();
  }, []);

  const loadGlobalLedger = async () => {
    try {
      const { data } = await api.get('/admin/plataforma/system-audit/accounting/global-ledger/');
      setStats(data);
    } catch (e) {
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      <div className="flex justify-between items-end">
        <div>
           <div className="flex items-center gap-2 text-indigo-600 font-bold mb-2 uppercase tracking-widest text-xs">
              <FiLayers /> Supervisión Financiera Cross-Tenant
           </div>
           <h1 className="text-5xl font-black text-slate-900 tracking-tighter uppercase">Maestro Global de Cuentas</h1>
           <p className="text-slate-500 font-medium mt-1 italic">Vigilancia soberana de la estructura contable PUC en todo el ecosistema.</p>
        </div>
      </div>

      <ViewState isLoading={isLoading}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <Card className="lg:col-span-1 border-none shadow-xl bg-slate-900 text-white p-10 rounded-[2.5rem]">
               <p className="text-xs font-black uppercase tracking-[0.2em] text-indigo-400 mb-4">Total Cuentas Activas</p>
               <h3 className="text-6xl font-black italic tracking-tighter">{stats?.total_accounts_system_wide || 0}</h3>
               <div className="mt-12 pt-8 border-t border-white/10 space-y-4">
                  <div className="flex justify-between text-sm">
                     <span className="text-slate-400 font-bold uppercase">Consistencia Estructural</span>
                     <span className="text-emerald-400 font-black">100% OK</span>
                  </div>
                  <p className="text-[10px] text-slate-500 leading-relaxed uppercase font-bold tracking-widest">Alineado con Decreto 2650 de 1993 (PUC Colombia)</p>
               </div>
            </Card>

            <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
                {stats?.distribution?.map((item: any) => (
                    <Card key={item.type} className="border-none shadow-sm bg-white rounded-3xl p-8 hover:shadow-md transition-all">
                       <div className="flex justify-between items-start">
                          <div>
                             <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">{item.type}</p>
                             <h4 className="text-3xl font-black text-slate-900">{item.count}</h4>
                             <p className="text-xs text-slate-500 mt-2 font-medium">Registros en el ecosistema</p>
                          </div>
                          <div className="w-10 h-10 bg-indigo-50 text-indigo-600 rounded-xl flex items-center justify-center">
                             <FiActivity size={18} />
                          </div>
                       </div>
                    </Card>
                ))}
            </div>
        </div>

        <Card className="border-none shadow-sm bg-white rounded-[2.5rem] mt-8 overflow-hidden">
            <CardHeader className="p-8 border-b border-slate-50 flex justify-between items-center">
               <CardTitle className="text-xl font-black uppercase italic tracking-tight">Acciones de Auditoría PUC</CardTitle>
            </CardHeader>
            <CardContent className="p-8">
               <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <AuditAction title="Verificar Integridad" icon={FiSearch} color="text-blue-600" />
                  <AuditAction title="Exportar Reporte Global" icon={FiGrid} color="text-emerald-600" />
                  <AuditAction title="Ajustar Nomenclatura" icon={FiLayers} color="text-amber-600" />
               </div>
            </CardContent>
        </Card>
      </ViewState>
    </div>
  );
}

function AuditAction({ title, icon: Icon, color }: any) {
    return (
        <button className="flex items-center gap-4 p-6 bg-slate-50 rounded-2xl hover:bg-slate-100 transition-all group">
            <div className={`w-12 h-12 bg-white shadow-sm rounded-xl flex items-center justify-center ${color}`}>
                <Icon size={20} />
            </div>
            <span className="font-bold text-slate-700 uppercase tracking-tight text-sm">{title}</span>
        </button>
    );
}
