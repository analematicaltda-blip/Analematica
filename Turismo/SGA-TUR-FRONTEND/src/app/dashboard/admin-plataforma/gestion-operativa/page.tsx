'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import {
  FiGrid,
  FiTruck,
  FiBriefcase,
  FiMap,
  FiActivity,
  FiBox,
  FiUsers,
  FiSearch
} from 'react-icons/fi';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

export default function AdminGestionOperativaPage() {
  const specializedModules = [
    { title: 'Hoteles', icon: FiBriefcase, count: 12, status: 'Operational' },
    { title: 'Restaurantes', icon: FiBox, count: 24, status: 'Operational' },
    { title: 'Agencias', icon: FiMap, count: 8, status: 'Operational' },
    { title: 'Transporte', icon: FiTruck, count: 5, status: 'Operational' },
  ];

  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Supervisión Operativa Global</h1>
          <p className="text-slate-500 mt-2">Monitoreo de la capacidad instalada y oferta de servicios del ecosistema.</p>
        </div>
        <div className="relative">
           <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
           <input
             type="text"
             placeholder="Buscar prestador..."
             className="pl-12 pr-6 py-3 bg-white border border-slate-200 rounded-2xl text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none w-80 shadow-sm"
           />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
         {specializedModules.map((mod, i) => (
           <Card key={i} className="border-none shadow-sm hover:shadow-lg transition-all bg-white group">
              <CardContent className="p-8 text-center">
                 <div className="w-16 h-16 bg-slate-50 text-indigo-600 rounded-3xl flex items-center justify-center mx-auto mb-6 group-hover:bg-indigo-600 group-hover:text-white transition-all">
                    <mod.icon size={32} />
                 </div>
                 <h3 className="text-xl font-bold text-slate-900">{mod.title}</h3>
                 <p className="text-4xl font-black text-indigo-600 mt-2">{mod.count}</p>
                 <Badge variant="outline" className="mt-4 border-emerald-100 text-emerald-600 bg-emerald-50">
                    {mod.status}
                 </Badge>
              </CardContent>
           </Card>
         ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
         <Card className="lg:col-span-2 border-none shadow-sm bg-white overflow-hidden">
            <CardHeader className="p-8 border-b border-slate-50 flex flex-row items-center justify-between">
               <CardTitle className="text-xl font-bold flex items-center gap-2">
                  <FiUsers className="text-indigo-600" /> Carga del Ecosistema
               </CardTitle>
               <Button variant="ghost" className="text-indigo-600 font-bold">Ver Mapa de Calor</Button>
            </CardHeader>
            <CardContent className="p-8">
               <div className="space-y-10">
                  <div>
                     <div className="flex justify-between mb-4">
                        <span className="font-bold text-slate-700">Ocupación Hotelera Consolidada</span>
                        <span className="font-black text-indigo-600">68%</span>
                     </div>
                     <div className="h-4 bg-slate-100 rounded-full overflow-hidden">
                        <div className="h-full bg-indigo-500 w-[68%]" />
                     </div>
                  </div>
                  <div>
                     <div className="flex justify-between mb-4">
                        <span className="font-bold text-slate-700">Demanda de Guías de Turismo</span>
                        <span className="font-black text-emerald-600">92%</span>
                     </div>
                     <div className="h-4 bg-slate-100 rounded-full overflow-hidden">
                        <div className="h-full bg-emerald-500 w-[92%]" />
                     </div>
                  </div>
               </div>
            </CardContent>
         </Card>

         <Card className="border-none shadow-sm bg-slate-900 text-white p-8">
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
               <FiActivity className="text-indigo-400" /> Alertas Operativas
            </h3>
            <div className="space-y-6">
               <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                  <p className="text-xs font-black text-amber-400 uppercase tracking-widest mb-1">Logística</p>
                  <p className="text-sm font-bold leading-tight">Escasez de guías bilingües detectada para el próximo fin de semana festivo.</p>
               </div>
               <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                  <p className="text-xs font-black text-indigo-400 uppercase tracking-widest mb-1">Inventario</p>
                  <p className="text-sm font-bold leading-tight">Incremento inusual de stock en 4 restaurantes del sector centro.</p>
               </div>
               <Button className="w-full bg-indigo-600 hover:bg-indigo-500 font-black py-4 mt-4">
                  Optimizar Recursos
               </Button>
            </div>
         </Card>
      </div>
    </div>
  );
}
