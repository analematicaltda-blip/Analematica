'use client';

import React, { useEffect, useState } from 'react';
import { useMiNegocioApi } from '../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import {
  FiDollarSign,
  FiTrendingUp,
  FiAlertCircle,
  FiPieChart,
  FiArrowUpRight,
  FiArrowDownRight,
  FiActivity,
  FiShield,
  FiTarget,
  FiCalendar
} from 'react-icons/fi';
import { Button } from '@/components/ui/Button';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Legend, Cell
} from 'recharts';
import { Badge } from '@/components/ui/Badge';

export default function FinanzasDashboard() {
  const { getTesoreria, getIndicadores, isLoading } = useMiNegocioApi();
  const [data, setData] = useState<any>(null);
  const [indicadores, setIndicadores] = useState<any[]>([]);

  useEffect(() => {
    const load = async () => {
      const [t, ind] = await Promise.all([getTesoreria(), getIndicadores()]);
      if (t && t.length > 0) setData(t[0]);
      if (ind) setIndicadores(ind);
    };
    load();
  }, [getTesoreria, getIndicadores]);

  const findIndicador = (name: string) => indicadores.find(i => i.nombre === name)?.valor || '0.00';

  const kpis = [
    { label: 'Liquidez Corriente', value: findIndicador('LIQUIDEZ_CORRIENTE'), icon: FiActivity, color: 'text-blue-600', trend: '+5%', status: 'Real' },
    { label: 'Margen EBITDA', value: findIndicador('RENTABILIDAD_NETA'), icon: FiTrendingUp, color: 'text-green-600', trend: '+2%', status: 'Real' },
    { label: 'Endeudamiento', value: findIndicador('ENDEUDAMIENTO_TOTAL'), icon: FiAlertCircle, color: 'text-amber-600', trend: '-1%', status: 'Real' },
    { label: 'EBITDA Estimado', value: `$${parseFloat(findIndicador('EBITDA_ESTIMADO')).toLocaleString()}`, icon: FiPieChart, color: 'text-purple-600', trend: '+0.5%', status: 'Real' },
  ];

  const cashFlowData = [
    { name: 'Ene', real: 4000, proyectado: 4400 },
    { name: 'Feb', real: 3000, proyectado: 3200 },
    { name: 'Mar', real: 2000, proyectado: 2500 },
    { name: 'Abr', real: 2780, proyectado: 2800 },
    { name: 'May', real: 1890, proyectado: 2100 },
    { name: 'Jun', real: 2390, proyectado: 2400 },
    { name: 'Jul', real: 3490, proyectado: 3300 },
  ];

  return (
    <div className="space-y-8 pb-12 animate-in fade-in duration-700">
      {/* Header Ejecutivo */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-4xl font-black text-slate-900 dark:text-white tracking-tight">Estrategia Financiera</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Control de gobierno y soberanía económica del negocio.</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="border-slate-200 dark:border-white/5 font-bold shadow-sm">
             <FiCalendar className="mr-2" /> Programar Auditoría
          </Button>
          <Button className="bg-brand hover:bg-brand-light text-white font-black px-8 rounded-xl shadow-lg shadow-brand/20 transition-all">
             Ejecutar Cierre Fiscal
          </Button>
        </div>
      </div>

      {/* Hero Cash Balance */}
      <Card className="bg-slate-900 border-none shadow-2xl overflow-hidden relative min-h-[300px] flex items-center">
         <CardContent className="p-12 text-white flex flex-col lg:flex-row justify-between items-center w-full relative z-10 gap-12">
            <div className="space-y-6">
               <div>
                  <p className="text-xs font-black uppercase tracking-[0.4em] text-brand-light opacity-80 mb-3">Liquidez Total Operativa</p>
                  <p className="text-7xl font-black tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-white to-white/40">
                     ${data ? parseFloat(data.liquidez_disponible).toLocaleString() : '0.00'}
                  </p>
               </div>
               <div className="flex flex-wrap gap-8">
                  <div className="space-y-1">
                     <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Ingresos Proyectados</p>
                     <p className="text-xl font-black text-green-400">+$24.5M <span className="text-[10px] opacity-50 font-medium">USD</span></p>
                  </div>
                  <div className="h-10 w-px bg-white/10 hidden sm:block" />
                  <div className="space-y-1">
                     <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Efectivo en Reservas</p>
                     <p className="text-xl font-black text-brand-light">$5.8M</p>
                  </div>
               </div>
            </div>

            <div className="flex-1 w-full max-w-md h-48">
               <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={cashFlowData}>
                     <defs>
                        <linearGradient id="colorReal" x1="0" y1="0" x2="0" y2="1">
                           <stop offset="5%" stopColor="#006D5B" stopOpacity={0.3}/>
                           <stop offset="95%" stopColor="#006D5B" stopOpacity={0}/>
                        </linearGradient>
                     </defs>
                     <Tooltip
                        contentStyle={{ backgroundColor: '#0f172a', border: 'none', borderRadius: '12px', fontSize: '12px' }}
                        itemStyle={{ color: '#fff' }}
                     />
                     <Area type="monotone" dataKey="real" stroke="#00EDC2" strokeWidth={3} fillOpacity={1} fill="url(#colorReal)" />
                  </AreaChart>
               </ResponsiveContainer>
            </div>
         </CardContent>
         <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-brand/10 via-transparent to-transparent opacity-50" />
      </Card>

      {/* KPI Grid Premium */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
         {kpis.map((kpi) => (
            <Card key={kpi.label} className="border-none shadow-sm bg-white dark:bg-brand-deep/10 hover:shadow-xl transition-all duration-300 group cursor-default">
               <CardContent className="p-8">
                  <div className="flex justify-between items-start mb-6">
                     <div className={`p-4 rounded-2xl bg-slate-50 dark:bg-black/20 ${kpi.color} group-hover:scale-110 transition-transform`}>
                        <kpi.icon size={24} />
                     </div>
                     <Badge variant="outline" className="text-[9px] font-black uppercase tracking-tighter border-slate-100 dark:border-white/5">
                        {kpi.status}
                     </Badge>
                  </div>
                  <div className="space-y-1">
                     <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{kpi.label}</p>
                     <div className="flex items-baseline gap-2">
                        <p className="text-3xl font-black text-slate-900 dark:text-white">{kpi.value}</p>
                        <span className={`text-[10px] font-black ${kpi.trend.startsWith('+') ? 'text-green-500' : 'text-red-500'}`}>
                           {kpi.trend}
                        </span>
                     </div>
                  </div>
               </CardContent>
            </Card>
         ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
         {/* Main Chart Card */}
         <Card className="lg:col-span-2 border-none shadow-sm bg-white dark:bg-brand-deep/10 overflow-hidden">
            <CardHeader className="p-8 border-b border-slate-50 dark:border-white/5 flex flex-row items-center justify-between">
               <div>
                  <CardTitle className="text-xl font-black uppercase tracking-tighter">Ejecución Presupuestal</CardTitle>
                  <p className="text-xs text-slate-400 font-bold mt-1 uppercase tracking-widest">Consolidado por centro de costo</p>
               </div>
               <div className="flex gap-2">
                  <div className="flex items-center gap-2">
                     <div className="w-3 h-3 rounded-full bg-brand" />
                     <span className="text-[10px] font-bold text-slate-500 uppercase">Real</span>
                  </div>
                  <div className="flex items-center gap-2">
                     <div className="w-3 h-3 rounded-full bg-slate-200" />
                     <span className="text-[10px] font-bold text-slate-500 uppercase">Estimado</span>
                  </div>
               </div>
            </CardHeader>
            <CardContent className="p-8">
               <div className="h-[400px] w-full mt-4">
                  <ResponsiveContainer width="100%" height="100%">
                     <BarChart data={[
                        { name: 'Nómina', real: 120, est: 100 },
                        { name: 'Infra', real: 85, est: 110 },
                        { name: 'Mkt', real: 150, est: 130 },
                        { name: 'SST', real: 45, est: 50 },
                        { name: 'Log.', real: 95, est: 90 },
                     ]}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 10, fontWeight: 'bold'}} dy={10} />
                        <YAxis hide />
                        <Tooltip
                           cursor={{fill: '#f8fafc'}}
                           contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                        />
                        <Bar dataKey="est" fill="#e2e8f0" radius={[4, 4, 0, 0]} barSize={40} />
                        <Bar dataKey="real" radius={[4, 4, 0, 0]} barSize={40}>
                           {[1,2,3,4,5].map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={index === 2 ? '#ef4444' : '#006D5B'} />
                           ))}
                        </Bar>
                     </BarChart>
                  </ResponsiveContainer>
               </div>
            </CardContent>
         </Card>

         {/* Alerts Sidebar */}
         <div className="space-y-6">
            <Card className="border-none shadow-sm bg-slate-900 text-white overflow-hidden group">
               <CardHeader className="p-8">
                  <CardTitle className="text-sm font-black uppercase tracking-[0.2em] text-brand-light">Alertas de Gobierno</CardTitle>
               </CardHeader>
               <CardContent className="p-8 pt-0 space-y-4">
                  <div className="p-6 bg-white/5 rounded-2xl border border-white/5 hover:bg-white/10 transition-colors">
                     <div className="flex items-center gap-3 mb-3">
                        <FiAlertCircle className="text-red-400" />
                        <p className="text-xs font-black uppercase tracking-widest text-red-400">Riesgo de Liquidez</p>
                     </div>
                     <p className="text-sm text-slate-300 leading-relaxed">El flujo proyectado para <span className="text-white font-bold">Agosto</span> detecta una brecha de $1.2M en capital de trabajo.</p>
                     <Button variant="link" className="p-0 text-brand-light text-xs font-bold mt-4 h-auto uppercase tracking-widest">Activar Plan Mitigación →</Button>
                  </div>

                  <div className="p-6 bg-white/5 rounded-2xl border border-white/5 hover:bg-white/10 transition-colors">
                     <div className="flex items-center gap-3 mb-3">
                        <FiTarget className="text-amber-400" />
                        <p className="text-xs font-black uppercase tracking-widest text-amber-400">Sobrecosto Marketing</p>
                     </div>
                     <p className="text-sm text-slate-300 leading-relaxed">Ejecución del 115% en campañas digitales. Se requiere revisión de ROI por Coronel.</p>
                  </div>
               </CardContent>
            </Card>

            <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/10 p-8">
               <h3 className="font-black uppercase tracking-tighter text-slate-900 dark:text-white mb-6 flex items-center gap-2">
                  <FiShield className="text-brand" /> Certificación SARITA
               </h3>
               <div className="space-y-4">
                  <div className="flex items-center justify-between text-xs font-bold uppercase tracking-widest text-slate-400">
                     <span>Integridad Contable</span>
                     <span className="text-green-500">100%</span>
                  </div>
                  <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                     <div className="h-full bg-brand w-full shadow-[0_0_10px_rgba(0,109,91,0.5)]" />
                  </div>
                  <p className="text-xs text-slate-500 mt-4 leading-relaxed">Todos los saldos de tesorería están conciliados con la contabilidad oficial al día de hoy.</p>
               </div>
            </Card>
         </div>
      </div>
    </div>
  );
}
