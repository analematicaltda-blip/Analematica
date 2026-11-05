'use client';

import React, { useEffect, useState } from 'react';
import api from '@/services/api';
import { toast } from 'react-hot-toast';
import {
  FiDollarSign,
  FiTrendingUp,
  FiUsers,
  FiPieChart,
  FiArrowUpRight,
  FiArrowDownRight,
  FiActivity,
  FiZap,
  FiShield
} from 'react-icons/fi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';

export default function RentabilidadPage() {
  const [data, setData] = useState<any>(null);
  const [roiData, setRoiData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [summaryRes, roiRes] = await Promise.all([
        api.get('/admin/finanzas/dashboard/'),
        api.get('/admin/finanzas/dashboard/roi_analysis/')
      ]);
      setData(summaryRes.data);
      setRoiData(roiRes.data);
    } catch (error) {
      // toast.error("Error al cargar métricas financieras.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-slate-100 pb-8">
        <div>
          <h1 className="text-4xl font-black text-slate-900 dark:text-white tracking-tighter uppercase leading-none mb-2">Gobierno de Rentabilidad Sistémica</h1>
          <p className="text-slate-500 dark:text-slate-400 text-lg">Métricas de eficiencia económica: ROI, CAC y LTV en tiempo real.</p>
        </div>
        <div className="flex gap-4">
           <Button variant="outline" className="border-slate-200 dark:border-white/5 font-black text-xs uppercase tracking-widest px-8">
              Simular Escenarios
           </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
         <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-10 overflow-hidden relative">
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 italic">Capacidad Operativa</p>
            <h3 className="text-5xl font-black text-slate-900 dark:text-white">{data?.summary.total_sessions || '0'}</h3>
            <p className="mt-4 text-xs text-indigo-600 font-bold flex items-center gap-2">
               <FiUsers /> Sesiones de Voz SADI
            </p>
         </Card>

         <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-10 overflow-hidden relative">
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 italic">Gasto en Adquisición</p>
            <h3 className="text-5xl font-black text-red-600">${data?.summary.total_adq_costs.toFixed(2) || '0.00'}</h3>
            <p className="mt-4 text-xs text-slate-400 font-bold uppercase tracking-widest">Inversión en Cómputo IA</p>
         </Card>

         <Card className="border-none shadow-xl bg-slate-900 text-white p-10 overflow-hidden relative group">
            <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:scale-110 transition-transform duration-700">
               <FiTrendingUp size={120} />
            </div>
            <p className="text-brand-light font-black uppercase tracking-widest text-[10px] mb-2 italic">Margen de Eficiencia</p>
            <h3 className="text-5xl font-black text-emerald-400">${data?.summary.avg_cac.toFixed(2) || '0.00'}</h3>
            <p className="mt-4 text-xs text-slate-400 font-bold">CAC Promedio por Prospecto</p>
         </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
         <Card className="lg:col-span-2 border-none shadow-sm bg-white dark:bg-brand-deep/10 overflow-hidden">
            <CardHeader className="p-8 border-b border-slate-50 dark:border-white/5 flex flex-row items-center justify-between">
               <CardTitle className="text-xl font-bold flex items-center gap-3 text-brand italic">
                  <FiActivity /> ROI por Segmento del Ecosistema
               </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
               <div className="divide-y divide-slate-50 dark:divide-white/5">
                  {roiData.map((roi, i) => (
                    <div key={i} className="p-10 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-white/5 transition-all group">
                       <div className="flex items-center gap-8">
                          <div className="w-16 h-16 rounded-2xl bg-slate-100 dark:bg-black/20 flex items-center justify-center text-slate-400 group-hover:text-brand transition-colors">
                             <FiPieChart size={32} />
                          </div>
                          <div>
                             <h4 className="text-xl font-black text-slate-900 dark:text-white uppercase tracking-tighter mb-2 italic">{roi.dimension}</h4>
                             <div className="flex gap-6">
                                <span className="text-xs font-bold text-slate-400">CAC: <span className="text-red-500">${roi.cac}</span></span>
                                <span className="text-xs font-bold text-slate-400">LTV: <span className="text-emerald-500">${roi.ltv}</span></span>
                             </div>
                          </div>
                       </div>
                       <div className="text-right">
                          <p className={`text-4xl font-black italic ${roi.roi > 5 ? 'text-emerald-500' : 'text-amber-500'}`}>
                             {roi.roi}x
                          </p>
                          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mt-1">Sovereign ROI</p>
                       </div>
                    </div>
                  ))}
                  {roiData.length === 0 && (
                     <div className="p-32 text-center">
                        <FiZap size={48} className="mx-auto text-slate-200 mb-6" />
                        <p className="text-slate-400 font-bold italic uppercase tracking-widest text-sm">Consolidando flujos financieros...</p>
                     </div>
                  )}
               </div>
            </CardContent>
         </Card>

         <div className="space-y-6">
            <Card className="border-none shadow-xl bg-indigo-600 text-white p-10 rounded-3xl overflow-hidden relative">
               <div className="absolute -left-10 -bottom-10 opacity-20 group-hover:scale-125 transition-transform duration-700">
                  <FiShield size={250} />
               </div>
               <h3 className="text-2xl font-black mb-4 italic">Alerta de Soberanía</h3>
               <p className="text-indigo-100 leading-relaxed font-medium">El CAC del segmento "Hotelería" ha incrementado un 12%. SADI recomienda pausar campañas de voz automatizadas en el Nodo Meta.</p>
               <Button className="w-full bg-white text-indigo-600 font-black py-4 mt-8 rounded-xl shadow-2xl">
                  Aplicar Restricción
               </Button>
            </Card>

            <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-10 rounded-3xl">
               <h4 className="font-black text-slate-900 dark:text-white uppercase tracking-widest text-xs mb-8">Evolución del LTV</h4>
               <div className="space-y-10">
                  <div>
                     <div className="flex justify-between mb-2">
                        <span className="text-xs font-bold text-slate-500 uppercase">Proyectado Q3</span>
                        <span className="text-sm font-black text-emerald-500">+18%</span>
                     </div>
                     <div className="h-1.5 bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full bg-brand w-[65%]" />
                     </div>
                  </div>
                  <div>
                     <div className="flex justify-between mb-2">
                        <span className="text-xs font-bold text-slate-500 uppercase">Tasa de Retención</span>
                        <span className="text-sm font-black text-indigo-500">94.2%</span>
                     </div>
                     <div className="h-1.5 bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full bg-indigo-500 w-[94%]" />
                     </div>
                  </div>
               </div>
            </Card>
         </div>
      </div>
    </div>
  );
}
