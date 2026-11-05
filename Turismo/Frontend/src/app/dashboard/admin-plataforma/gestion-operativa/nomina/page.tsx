'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import {
  FiUsers,
  FiFileText,
  FiTrendingUp,
  FiActivity,
  FiShield,
  FiCheckCircle,
  FiSearch
} from 'react-icons/fi';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

export default function AdminNominaSistemicaPage() {
  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight uppercase">Control de Nómina y Talento Humano</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-2">Visibilidad transversal del capital humano en el ecosistema.</p>
        </div>
        <div className="flex gap-4">
           <Button className="bg-brand text-white font-black px-8 py-6 rounded-2xl">
              Reporte Consolidado PILA
           </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
         <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8">
            <div className="flex justify-between items-start mb-6">
               <div className="p-4 bg-indigo-50 text-indigo-600 rounded-2xl">
                  <FiUsers size={28} />
               </div>
            </div>
            <p className="text-slate-400 font-bold uppercase tracking-widest text-xs mb-2">Empleados en Red</p>
            <h3 className="text-4xl font-black text-slate-900 dark:text-white">1,248</h3>
            <p className="mt-4 text-xs text-emerald-600 font-bold">+3.2% este trimestre</p>
         </Card>

         <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8">
            <div className="flex justify-between items-start mb-6">
               <div className="p-4 bg-emerald-50 text-emerald-600 rounded-2xl">
                  <FiCheckCircle size={28} />
               </div>
            </div>
            <p className="text-slate-400 font-bold uppercase tracking-widest text-xs mb-2">Cumplimiento Seguridad Social</p>
            <h3 className="text-4xl font-black text-slate-900 dark:text-white">98.5%</h3>
            <p className="mt-4 text-xs text-slate-400 font-bold tracking-tighter">Monitoreo automatizado por SADI</p>
         </Card>

         <Card className="border-none shadow-sm bg-slate-900 text-white p-8 overflow-hidden relative">
            <div className="absolute right-0 bottom-0 p-8 opacity-10">
               <FiShield size={120} />
            </div>
            <p className="text-brand-light font-black uppercase tracking-widest text-xs mb-4">Gobernanza Laboral</p>
            <h3 className="text-3xl font-black leading-tight">Auditoría de Contratos Activa</h3>
            <Button variant="ghost" className="mt-6 text-brand-light font-bold p-0 hover:bg-transparent">Ver Alertas →</Button>
         </Card>
      </div>

      <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/10 overflow-hidden">
         <CardHeader className="p-8 border-b border-slate-50 dark:border-white/5 flex flex-row items-center justify-between">
            <CardTitle className="text-xl font-bold flex items-center gap-3">
               <FiActivity className="text-brand" /> Distribución de Costos Laborales por Sector
            </CardTitle>
            <div className="flex gap-2">
               <Badge className="bg-slate-100 text-slate-600 border-none font-bold">Gastronomía</Badge>
               <Badge className="bg-slate-100 text-slate-600 border-none font-bold">Hotelería</Badge>
               <Badge className="bg-brand text-white border-none font-bold">Todos</Badge>
            </div>
         </CardHeader>
         <CardContent className="p-12 text-center">
            <div className="max-w-md mx-auto">
               <FiFileText size={64} className="mx-auto text-slate-200 mb-6" />
               <h4 className="text-xl font-black text-slate-900 dark:text-white mb-2">Procesando Datos Transversales</h4>
               <p className="text-slate-500 mb-8">SADI está consolidando la información de nómina de los 42 prestadores verificados para generar el comparativo sectorial.</p>
               <div className="h-2 bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden">
                  <div className="h-full bg-brand w-[72%] animate-pulse" />
               </div>
            </div>
         </CardContent>
      </Card>
    </div>
  );
}
