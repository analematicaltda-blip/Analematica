'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import {
  FiBook,
  FiActivity,
  FiTrendingUp,
  FiAlertCircle,
  FiPieChart,
  FiBarChart,
  FiSearch
} from 'react-icons/fi';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

export default function AdminGestionContableSistemicaPage() {
  const accountHighlights = [
    { code: '1105', name: 'Caja General', status: 'AUDITED', drift: '0.00%' },
    { code: '4135', name: 'Comercio al por Mayor', status: 'PENDING', drift: '+0.12%' },
  ];

  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-slate-100 pb-8">
        <div>
          <h1 className="text-4xl font-black text-slate-900 dark:text-white tracking-tighter uppercase leading-none mb-2">Consolidado Contable Maestro</h1>
          <p className="text-slate-500 dark:text-slate-400 text-lg">Visión unificada del libro mayor sistémico y cumplimiento tributario.</p>
        </div>
        <div className="flex gap-3">
           <Button className="bg-slate-900 text-white font-black px-8 py-6 rounded-2xl shadow-xl">
              Cierre Sistémico
           </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
         <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8">
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Activos Red</p>
            <h3 className="text-3xl font-black text-slate-900 dark:text-white">$1.8M</h3>
         </Card>
         <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8">
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Pasivos Red</p>
            <h3 className="text-3xl font-black text-slate-900 dark:text-white">$420k</h3>
         </Card>
         <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8">
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Ingresos Brutos</p>
            <h3 className="text-3xl font-black text-emerald-600">$1.2M</h3>
         </Card>
         <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8 border-l-4 border-l-brand">
            <p className="text-[10px] font-black text-brand uppercase tracking-widest mb-4">Patrimonio Neto</p>
            <h3 className="text-3xl font-black text-slate-900 dark:text-white">$1.38M</h3>
         </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
         <Card className="lg:col-span-2 border-none shadow-sm bg-white dark:bg-brand-deep/10 overflow-hidden">
            <CardHeader className="p-8 border-b border-slate-50 dark:border-white/5 flex flex-row items-center justify-between">
               <CardTitle className="text-xl font-bold flex items-center gap-3 italic text-brand">
                  <FiPieChart /> Estructura de Costos Agregada
               </CardTitle>
               <div className="flex gap-2">
                  <Badge className="bg-slate-100 text-slate-600 font-bold uppercase text-[9px] px-3 py-1">Semestral</Badge>
               </div>
            </CardHeader>
            <CardContent className="p-12 text-center">
               <div className="max-w-md mx-auto space-y-8">
                  <div className="w-48 h-48 rounded-full border-[16px] border-brand/10 border-t-brand mx-auto relative flex items-center justify-center">
                     <div className="text-center">
                        <p className="text-3xl font-black text-slate-900 dark:text-white leading-none">62%</p>
                        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Margen</p>
                     </div>
                  </div>
                  <p className="text-slate-500 font-medium leading-relaxed">El ecosistema presenta un margen de contribución saludable, liderado por el sector de Agencias y Guías.</p>
                  <Button variant="outline" className="w-full border-slate-100 dark:border-white/5 font-black uppercase text-xs tracking-widest py-4">
                     Desglose por Cuenta
                  </Button>
               </div>
            </CardContent>
         </Card>

         <div className="space-y-6">
            <Card className="border-none shadow-sm bg-slate-900 text-white p-8">
               <h3 className="text-lg font-black uppercase tracking-widest text-brand-light mb-6 flex items-center gap-2">
                  <FiAlertCircle /> Riesgos Fiscales
               </h3>
               <div className="space-y-6">
                  <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                     <p className="text-[10px] font-black text-amber-400 uppercase tracking-[0.2em] mb-1 italic">Nodo Gaitan</p>
                     <p className="text-sm font-bold">Desviación en reporte de IVA para 12 prestadores.</p>
                  </div>
                  <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                     <p className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.2em] mb-1 italic">Retenciones</p>
                     <p className="text-sm font-bold">Nueva normativa de retención en la fuente lista para aplicar.</p>
                  </div>
                  <Button className="w-full bg-indigo-600 hover:bg-indigo-500 font-black py-4 mt-6 rounded-xl transition-all shadow-lg shadow-indigo-600/30">
                     Ejecutar Validación IA
                  </Button>
               </div>
            </Card>

            <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8">
               <div className="flex items-center gap-2 mb-6">
                  <FiBarChart className="text-brand" />
                  <h4 className="font-bold text-slate-900 dark:text-white uppercase tracking-tighter italic">Top Cuentas Auditadas</h4>
               </div>
               <div className="space-y-4">
                  {accountHighlights.map((acc, i) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-slate-50 dark:bg-black/20 rounded-xl">
                       <span className="font-mono text-xs font-black text-brand">{acc.code}</span>
                       <span className="text-[10px] font-bold text-slate-500 uppercase">{acc.name}</span>
                       <span className="text-xs font-black text-emerald-500">{acc.drift}</span>
                    </div>
                  ))}
               </div>
            </Card>
         </div>
      </div>
    </div>
  );
}
