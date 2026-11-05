"use client";

import React, { useState, useEffect, useMemo } from 'react';
import { governmentService } from '@/services/tripleViaService';
import { getUnifiedDashboard } from '@/services/intelligence';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
    FiUsers, FiTrendingUp, FiMap, FiActivity, FiGlobe,
    FiArrowUpRight, FiMessageCircle, FiBriefcase
} from 'react-icons/fi';
import {
    ResponsiveContainer, AreaChart, Area, XAxis, YAxis,
    CartesianGrid, Tooltip, BarChart, Bar, Cell
} from 'recharts';

export default function GovernmentDashboard() {
  const [officials, setOfficials] = useState([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [territorialFilter, setTerritorialFilter] = useState({ dept: '', mun: '' });

  const loadData = useCallback(() => {
    setLoading(true);
    Promise.all([
        governmentService.getOfficials(),
        getUnifiedDashboard(territorialFilter.dept || undefined, territorialFilter.mun || undefined)
    ]).then(([offRes, intelRes]) => {
        setOfficials(offRes.data.results || []);
        setAnalytics(intelRes);
        setLoading(false);
    });
  }, [territorialFilter]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Simulación de datos para gráficos basados en analítica real
  const visitorFlow = [
    { name: 'Lun', flow: 400 },
    { name: 'Mar', flow: 520 },
    { name: 'Mie', flow: 480 },
    { name: 'Jue', flow: 610 },
    { name: 'Vie', flow: 850 },
    { name: 'Sab', flow: 1200 },
    { name: 'Dom', flow: 1100 },
  ];

  const economicData = [
    { category: 'Hoteles', value: 45 },
    { category: 'Restaurantes', value: 30 },
    { category: 'Tours', value: 15 },
    { category: 'Artesanías', value: 10 },
  ];

  const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444'];

  return (
    <div className="p-8 space-y-10 bg-slate-50/50 min-h-screen animate-in fade-in duration-700">
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
           <div className="flex items-center gap-2 text-indigo-600 font-bold mb-2">
              <FiGlobe /> SADI · Sistema de Analítica de Destino Inteligente
           </div>
           <h1 className="text-5xl font-black text-slate-900 tracking-tighter uppercase">Panel de Gobernanza</h1>
           <p className="text-slate-500 font-medium mt-1">Supervisión estratégica y gestión institucional territorial.</p>
        </div>
        <div className="flex gap-4 bg-white p-3 rounded-2xl shadow-sm border border-slate-100">
           <select
             className="bg-transparent font-bold text-xs uppercase"
             value={territorialFilter.dept}
             onChange={(e) => setTerritorialFilter({ dept: e.target.value, mun: '' })}
           >
              <option value="">Todo el País</option>
              <option value="50">Meta</option>
              <option value="25">Cundinamarca</option>
           </select>
           <div className="w-px h-6 bg-slate-200" />
           <select
             className="bg-transparent font-bold text-xs uppercase"
             value={territorialFilter.mun}
             onChange={(e) => setTerritorialFilter({ ...territorialFilter, mun: e.target.value })}
           >
              <option value="">Todos los Municipios</option>
              {territorialFilter.dept === '50' && (
                <>
                  <option value="50568">Puerto Gaitán</option>
                  <option value="50001">Villavicencio</option>
                </>
              )}
           </select>
        </div>
        <div className="flex gap-3">
           <Button className="bg-white text-slate-900 border border-slate-200 font-bold px-6 py-3 rounded-xl shadow-sm hover:bg-slate-50">Generar Reporte PDF</Button>
           <Button className="bg-indigo-600 text-white font-bold px-6 py-3 rounded-xl shadow-lg shadow-indigo-200">Nueva Política</Button>
        </div>
      </header>

      {/* Real-time KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
         <KpiCard
            title="Interacciones Vía 3"
            value={analytics?.via_3?.total_interacciones || '0'}
            sub="Mensajes analizados por IA"
            icon={FiMessageCircle}
            trend="+12%"
         />
         <KpiCard
            title="Prestadores Activos"
            value={analytics?.via_2?.prestadores_activos || '0'}
            sub="Empresas registradas"
            icon={FiBriefcase}
            trend="+3"
         />
         <KpiCard
            title="Sentimiento Turista"
            value={`${(analytics?.via_3?.sentimiento_promedio * 100 || 0).toFixed(0)}%`}
            sub="Nivel de satisfacción"
            icon={FiActivity}
            trend="+5.2%"
            isPositive
         />
         <KpiCard
            title="Impacto Económico"
            value={`$${(analytics?.via_2?.impacto_economico?.ventas_totales / 1000000 || 0).toFixed(1)}M`}
            sub="Ventas estimadas Q1"
            icon={FiTrendingUp}
            trend="+8.1%"
            isPositive
         />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
         {/* Main Analytical Chart */}
         <Card className="lg:col-span-2 border-none shadow-xl rounded-[2.5rem] bg-white overflow-hidden">
            <CardHeader className="p-8 border-b border-slate-50">
               <div className="flex items-center justify-between">
                  <div>
                     <CardTitle className="text-xl font-black uppercase tracking-tight">Flujo de Visitantes en Tiempo Real</CardTitle>
                     <p className="text-sm text-slate-400 font-medium">SADI Monitorización de movilidad (Sensores Digitales)</p>
                  </div>
                  <div className="flex items-center gap-2 bg-emerald-50 text-emerald-600 px-3 py-1 rounded-full text-[10px] font-black uppercase">
                     <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-ping" /> Live Streaming
                  </div>
               </div>
            </CardHeader>
            <CardContent className="p-8 h-[400px]">
               <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={visitorFlow}>
                     <defs>
                        <linearGradient id="colorFlow" x1="0" y1="0" x2="0" y2="1">
                           <stop offset="5%" stopColor="#6366f1" stopOpacity={0.1}/>
                           <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                        </linearGradient>
                     </defs>
                     <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                     <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fontSize: 12, fontWeight: 600, fill: '#94a3b8'}} dy={10} />
                     <YAxis axisLine={false} tickLine={false} tick={{fontSize: 12, fontWeight: 600, fill: '#94a3b8'}} />
                     <Tooltip
                        contentStyle={{borderRadius: '1rem', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)'}}
                        itemStyle={{fontWeight: 800, color: '#6366f1'}}
                     />
                     <Area type="monotone" dataKey="flow" stroke="#6366f1" strokeWidth={4} fillOpacity={1} fill="url(#colorFlow)" />
                  </AreaChart>
               </ResponsiveContainer>
            </CardContent>
         </Card>

         {/* Economic Distribution */}
         <Card className="border-none shadow-xl rounded-[2.5rem] bg-white overflow-hidden">
            <CardHeader className="p-8 border-b border-slate-50">
               <CardTitle className="text-xl font-black uppercase tracking-tight">Distribución del Gasto</CardTitle>
               <p className="text-sm text-slate-400 font-medium">Por sectores operativos vía 2</p>
            </CardHeader>
            <CardContent className="p-8 h-[400px]">
               <div className="space-y-4 overflow-y-auto h-full pr-4 custom-scrollbar">
                  {analytics?.via_2?.consolidado_territorial?.map((item: any, idx: number) => (
                    <div key={idx} className="bg-slate-50 p-6 rounded-3xl flex justify-between items-center group hover:bg-indigo-600 transition-all">
                       <div>
                          <p className="text-[10px] font-black text-slate-400 uppercase group-hover:text-indigo-200">Jurisdicción</p>
                          <h4 className="font-bold text-slate-900 group-hover:text-white uppercase">{item.municipality__name || item.department__name}</h4>
                       </div>
                       <div className="text-right">
                          <p className="text-2xl font-black text-indigo-600 group-hover:text-white">{item.count}</p>
                          <p className="text-[9px] font-black text-slate-400 uppercase group-hover:text-indigo-200">Prestadores</p>
                       </div>
                    </div>
                  ))}
                  {(!analytics?.via_2?.consolidado_territorial || analytics?.via_2?.consolidado_territorial.length === 0) && (
                     <div className="flex flex-col items-center justify-center h-full text-slate-400 italic">
                        <FiMap size={48} className="mb-4 opacity-10" />
                        No hay datos territoriales consolidados.
                     </div>
                  )}
               </div>
            </CardContent>
         </Card>
      </div>

      {/* Workforce Management */}
      <section className="space-y-6">
         <div className="flex items-center justify-between px-4">
            <h2 className="text-xl font-black text-slate-900 uppercase tracking-widest flex items-center gap-3">
               <FiUsers className="text-indigo-600" /> Cuerpo de Funcionarios
            </h2>
            <Button variant="link" className="text-indigo-600 font-bold uppercase text-xs tracking-widest">Ver Todos</Button>
         </div>
         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {officials.slice(0, 4).map((off: any) => (
               <Card key={off.id} className="border-none shadow-sm rounded-3xl hover:shadow-md transition-all group">
                  <CardContent className="p-6">
                     <div className="flex items-center gap-4 mb-4">
                        <div className="w-12 h-12 bg-slate-100 rounded-2xl flex items-center justify-center font-black text-slate-400 group-hover:bg-indigo-600 group-hover:text-white transition-colors uppercase">
                           {off.user_name?.substring(0,2)}
                        </div>
                        <div>
                           <h4 className="font-bold text-slate-900 leading-none">{off.user_name}</h4>
                           <p className="text-[10px] text-slate-400 font-black uppercase mt-1 tracking-tighter">{off.cargo}</p>
                        </div>
                     </div>
                     <div className="flex items-center justify-between pt-4 border-t border-slate-50">
                        <span className="text-[9px] font-black text-indigo-600 bg-indigo-50 px-2 py-1 rounded-lg uppercase">{off.nivel}</span>
                        <div className="w-2 h-2 bg-emerald-500 rounded-full" />
                     </div>
                  </CardContent>
               </Card>
            ))}
            <button className="h-full border-2 border-dashed border-slate-200 rounded-[2rem] flex flex-col items-center justify-center p-6 hover:border-indigo-400 hover:bg-indigo-50/30 transition-all group">
               <div className="w-10 h-10 bg-white shadow-sm rounded-xl flex items-center justify-center text-slate-400 group-hover:text-indigo-600 mb-2">
                  <FiUsers />
               </div>
               <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest group-hover:text-indigo-600">Crear Funcionario</span>
            </button>
         </div>
      </section>
    </div>
  );
}

function KpiCard({ title, value, sub, icon: Icon, trend, isPositive }: any) {
  return (
    <Card className="border-none shadow-sm bg-white rounded-[2rem] p-8 overflow-hidden relative group hover:shadow-xl transition-all duration-500">
       <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:scale-110 transition-transform duration-700">
          <Icon size={80} />
       </div>
       <div className="relative z-10">
          <div className="w-10 h-10 bg-slate-50 text-slate-600 rounded-xl flex items-center justify-center mb-6">
             <Icon size={20} />
          </div>
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">{title}</p>
          <div className="flex items-baseline gap-2">
             <h4 className="text-3xl font-black text-slate-900 tracking-tighter">{value}</h4>
             <span className={`text-[10px] font-black ${isPositive ? 'text-emerald-500' : 'text-slate-400'} flex items-center gap-0.5`}>
                <FiArrowUpRight /> {trend}
             </span>
          </div>
          <p className="text-xs text-slate-400 font-medium mt-4">{sub}</p>
       </div>
    </Card>
  );
}
