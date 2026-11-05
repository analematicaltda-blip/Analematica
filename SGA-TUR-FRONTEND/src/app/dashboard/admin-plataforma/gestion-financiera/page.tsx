'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import {
  FiDollarSign,
  FiTrendingUp,
  FiTrendingDown,
  FiPieChart,
  FiActivity,
  FiShield,
  FiArrowUpRight,
  FiCreditCard
} from 'react-icons/fi';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

export default function AdminGestionFinancieraPage() {
  const nodeFinancials = [
    { name: 'Nodo Puerto Gaitán', revenue: '$85.4k', growth: '+14%', health: 'HIGH' },
    { name: 'Nodo Meta Regional', revenue: '$124.0k', growth: '+8%', health: 'MEDIUM' },
    { name: 'Nodo Nacional', revenue: '$342.1k', growth: '+22%', health: 'HIGH' },
  ];

  return (
    <div className="space-y-10 animate-in slide-in-from-bottom-8 duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-slate-100 pb-8">
        <div>
          <h1 className="text-4xl font-black text-slate-900 tracking-tighter uppercase">Inteligencia Financiera Sistémica</h1>
          <p className="text-slate-500 mt-2 text-lg">Control de flujo transaccional y rentabilidad de la red.</p>
        </div>
        <div className="flex gap-3">
           <Button variant="outline" className="border-slate-200 font-bold px-6">Exportar Reporte Maestro</Button>
           <Button className="bg-indigo-600 font-black px-8">Audit Now</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
         <Card className="border-none shadow-xl bg-slate-900 text-white overflow-hidden relative group">
            <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:scale-110 transition-transform duration-700">
               <FiPieChart size={150} />
            </div>
            <CardContent className="p-10 relative z-10">
               <p className="text-indigo-400 font-black uppercase tracking-widest text-xs mb-4">Volumen Transaccional Global</p>
               <h3 className="text-5xl font-black">$2.4M</h3>
               <div className="mt-8 flex items-center gap-3 text-emerald-400 font-bold">
                  <FiArrowUpRight />
                  <span>+18.4% vs Q1</span>
               </div>
            </CardContent>
         </Card>

         <Card className="border-none shadow-sm bg-white p-10">
            <div className="flex justify-between items-start mb-6">
               <div className="p-4 bg-emerald-50 text-emerald-600 rounded-3xl">
                  <FiTrendingUp size={28} />
               </div>
               <Badge className="bg-emerald-100 text-emerald-700 font-black">STABLE</Badge>
            </div>
            <p className="text-slate-400 font-bold uppercase tracking-widest text-xs mb-2">Tasa de Conversión ROI</p>
            <h3 className="text-4xl font-black text-slate-900">3.4x</h3>
            <p className="mt-4 text-sm text-slate-500 leading-relaxed">Promedio sistémico optimizado por SADI.</p>
         </Card>

         <Card className="border-none shadow-sm bg-white p-10">
            <div className="flex justify-between items-start mb-6">
               <div className="p-4 bg-indigo-50 text-indigo-600 rounded-3xl">
                  <FiShield size={28} />
               </div>
               <Badge className="bg-indigo-100 text-indigo-700 font-black">ACTIVE</Badge>
            </div>
            <p className="text-slate-400 font-bold uppercase tracking-widest text-xs mb-2">Solvencia de la Red</p>
            <h3 className="text-4xl font-black text-slate-900">92.4%</h3>
            <p className="mt-4 text-sm text-slate-500 leading-relaxed">Índice de liquidez inmediata agregada.</p>
         </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
         <Card className="lg:col-span-2 border-none shadow-sm bg-white rounded-[2rem] overflow-hidden">
            <CardHeader className="p-8 border-b border-slate-50">
               <CardTitle className="text-xl font-black flex items-center gap-3">
                  <FiActivity className="text-indigo-600" /> Rendimiento por Nodo Regional
               </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
               <div className="divide-y divide-slate-50">
                  {nodeFinancials.map((node, i) => (
                    <div key={i} className="p-8 flex items-center justify-between hover:bg-slate-50 transition-colors">
                       <div className="flex items-center gap-6">
                          <div className="w-12 h-12 bg-slate-100 rounded-2xl flex items-center justify-center text-slate-400">
                             <FiCreditCard size={20} />
                          </div>
                          <div>
                             <h4 className="font-black text-slate-900">{node.name}</h4>
                             <p className="text-xs text-slate-400 font-bold uppercase tracking-widest">Estado: Operativo</p>
                          </div>
                       </div>
                       <div className="text-right">
                          <p className="text-xl font-black text-slate-900">{node.revenue}</p>
                          <p className="text-sm font-bold text-emerald-600">{node.growth}</p>
                       </div>
                    </div>
                  ))}
               </div>
            </CardContent>
         </Card>

         <Card className="border-none shadow-xl bg-indigo-600 text-white rounded-[2rem] p-10 flex flex-col justify-between overflow-hidden relative">
            <div className="absolute -left-10 -bottom-10 opacity-20">
               <FiTrendingUp size={250} />
            </div>
            <div className="relative z-10">
               <h3 className="text-2xl font-black mb-4">Proyección de Ingresos Q3</h3>
               <p className="text-indigo-100 leading-relaxed">Basado en el crecimiento actual de afiliados y la optimización de CAC realizada por los agentes.</p>
            </div>
            <div className="relative z-10 mt-12">
               <h4 className="text-6xl font-black tracking-tighter">+$1.2M</h4>
               <p className="text-indigo-300 font-bold mt-2 uppercase tracking-[0.2em] text-xs">Expected Milestone</p>
               <Button className="w-full bg-white text-indigo-600 font-black py-6 rounded-2xl mt-8 hover:bg-indigo-50 transition-all">
                  Explorar Forecast
               </Button>
            </div>
         </Card>
      </div>
    </div>
  );
}
