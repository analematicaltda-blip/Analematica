'use client';

import React, { useState } from 'react';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  FiShield,
  FiRefreshCw,
  FiCheckCircle,
  FiAlertTriangle,
  FiSearch,
  FiFileText
} from 'react-icons/fi';
import { Badge } from '@/components/ui/Badge';

export default function ConciliacionBancariaPage() {
  const { isLoading } = useMiNegocioApi();
  const [step, setStep] = useState(1);

  return (
    <div className="space-y-8 py-8 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Conciliación Bancaria</h1>
          <p className="text-slate-500 mt-1">Cruce de información entre extractos bancarios y registros internos.</p>
        </div>
        <Button className="bg-slate-900 text-white font-black px-8 py-4 rounded-xl">
           <FiFileText className="mr-2" /> Subir Extracto PDF/Excel
        </Button>
      </div>

      {/* Progress Steps */}
      <div className="flex justify-between items-center bg-white p-6 rounded-3xl shadow-sm border border-slate-50 overflow-x-auto gap-12">
         {[
            { n: 1, l: 'Carga de Datos' },
            { n: 2, l: 'Cruce Automático' },
            { n: 3, l: 'Ajustes Manuales' },
            { n: 4, l: 'Certificación' },
         ].map((s) => (
            <div key={s.n} className="flex items-center gap-4 flex-shrink-0">
               <div className={`w-10 h-10 rounded-full flex items-center justify-center font-black text-sm transition-all ${step >= s.n ? 'bg-brand text-white shadow-lg shadow-brand/30' : 'bg-slate-100 text-slate-400'}`}>
                  {step > s.n ? <FiCheckCircle /> : s.n}
               </div>
               <span className={`text-xs font-black uppercase tracking-widest ${step >= s.n ? 'text-slate-900' : 'text-slate-300'}`}>{s.l}</span>
               {s.n < 4 && <div className="w-12 h-px bg-slate-100 hidden lg:block" />}
            </div>
         ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
         <div className="lg:col-span-2 space-y-6">
            <Card className="border-none shadow-sm bg-white overflow-hidden">
               <CardHeader className="p-8 border-b flex flex-row items-center justify-between">
                  <CardTitle className="text-xl font-black">Registros Pendientes</CardTitle>
                  <div className="relative">
                     <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                     <input type="text" placeholder="Buscar transacción..." className="pl-10 pr-4 py-2 bg-slate-50 rounded-lg text-xs outline-none" />
                  </div>
               </CardHeader>
               <CardContent className="p-0">
                  <div className="py-32 text-center opacity-20 flex flex-col items-center">
                     <FiRefreshCw size={64} className="animate-spin-slow mb-4" />
                     <p className="text-xl font-black uppercase tracking-tighter">Esperando extracto bancario</p>
                     <p className="text-sm">Cargue su archivo para iniciar el motor de cruce SARITA.</p>
                  </div>
               </CardContent>
            </Card>
         </div>

         <div className="space-y-6">
            <Card className="border-none shadow-sm bg-slate-900 text-white p-8">
               <h3 className="text-sm font-black uppercase tracking-[0.2em] text-brand-light mb-6">Resumen de Cuenta</h3>
               <div className="space-y-6">
                  <div>
                     <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Saldo en Libros</p>
                     <p className="text-2xl font-black">$12,450,000</p>
                  </div>
                  <div className="h-px bg-white/5" />
                  <div>
                     <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Saldo en Banco</p>
                     <p className="text-2xl font-black text-brand-light">$0</p>
                  </div>
                  <div className="p-6 bg-red-500/10 border border-red-500/20 rounded-2xl">
                     <div className="flex items-center gap-2 text-red-400 mb-2">
                        <FiAlertTriangle />
                        <span className="text-[10px] font-black uppercase tracking-widest">Discrepancia detectada</span>
                     </div>
                     <p className="text-lg font-black text-red-500">$12,450,000</p>
                  </div>
               </div>
            </Card>

            <Card className="border-none shadow-sm bg-white p-8">
               <h3 className="font-black uppercase tracking-tighter text-slate-900 mb-6 flex items-center gap-2">
                  <FiShield className="text-brand" /> Auditoría Inteligente
               </h3>
               <p className="text-sm text-slate-500 leading-relaxed mb-6">
                  SARITA utiliza algoritmos de coincidencia semántica para identificar transacciones incluso si las descripciones no coinciden exactamente.
               </p>
               <Button className="w-full bg-brand text-white font-black py-4 rounded-xl shadow-lg shadow-brand/20">Iniciar Cruce Automático</Button>
            </Card>
         </div>
      </div>
    </div>
  );
}
