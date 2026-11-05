'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FiSettings, FiLock, FiGlobe, FiDatabase, FiCpu } from 'react-icons/fi';
import { Switch } from '@/components/ui/Switch';

export default function ConfiguracionFinancieraPage() {
  return (
    <div className="space-y-8 py-8 animate-in fade-in duration-500 max-w-5xl mx-auto">
      <div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Configuración Financiera</h1>
        <p className="text-slate-500 mt-1">Ajustes de gobierno, límites de autoridad y parámetros del motor de proyecciones.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
         <div className="space-y-6">
            <div className="p-8 bg-slate-50 rounded-3xl border border-slate-100 space-y-4">
               <FiLock size={32} className="text-slate-400" />
               <h3 className="font-bold text-slate-800 uppercase tracking-tighter">Límites de Autoridad</h3>
               <p className="text-sm text-slate-500 leading-relaxed">Defina los montos máximos que cada nivel de la jerarquía puede autorizar sin escalamiento.</p>
            </div>
            <div className="p-8 bg-slate-50 rounded-3xl border border-slate-100 space-y-4">
               <FiCpu size={32} className="text-slate-400" />
               <h3 className="font-bold text-slate-800 uppercase tracking-tighter">Motor de IA</h3>
               <p className="text-sm text-slate-500 leading-relaxed">Configuración de modelos predictivos y sensibilidad de alertas de riesgo.</p>
            </div>
         </div>

         <div className="md:col-span-2 space-y-6">
            <Card className="border-none shadow-sm bg-white overflow-hidden">
               <CardHeader className="p-8 border-b">
                  <CardTitle className="text-xl font-black">Parámetros Globales</CardTitle>
               </CardHeader>
               <CardContent className="p-8 space-y-8">
                  <div className="flex items-center justify-between">
                     <div className="space-y-0.5">
                        <p className="font-bold text-slate-800">Cierre Automático de Caja</p>
                        <p className="text-sm text-slate-500">Permitir que SARITA consolide el flujo diario al finalizar la jornada.</p>
                     </div>
                     <Switch checked={true} />
                  </div>
                  <div className="h-px bg-slate-50" />
                  <div className="flex items-center justify-between">
                     <div className="space-y-0.5">
                        <p className="font-bold text-slate-800">Alertas de Sobrecosto</p>
                        <p className="text-sm text-slate-500">Notificar inmediatamente cuando un rubro excede el 90% del presupuesto.</p>
                     </div>
                     <Switch checked={true} />
                  </div>
                  <div className="h-px bg-slate-50" />
                  <div className="flex items-center justify-between">
                     <div className="space-y-0.5">
                        <p className="font-bold text-slate-800">Modo de Proyección Estricto</p>
                        <p className="text-sm text-slate-500">Utilizar solo datos confirmados para los escenarios conservadores.</p>
                     </div>
                     <Switch checked={false} />
                  </div>
               </CardContent>
            </Card>

            <Card className="border-none shadow-sm bg-slate-900 text-white p-8">
               <div className="flex items-center gap-4 mb-6">
                  <FiDatabase size={24} className="text-brand-light" />
                  <h3 className="text-lg font-black uppercase tracking-widest">Integridad de Datos</h3>
               </div>
               <p className="text-slate-400 text-sm mb-8">Sincronización forzada entre el ERP Quíntuple y el motor de finanzas tácticas.</p>
               <Button className="w-full bg-brand hover:bg-brand-light font-black py-4 rounded-xl transition-all">
                  Ejecutar Re-indexación Financiera
               </Button>
            </Card>
         </div>
      </div>
    </div>
  );
}
