'use client';
import React, { useEffect, useState } from 'react';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { FiBell, FiAlertCircle, FiCheck, FiMail, FiTrash2 } from 'react-icons/fi';

export default function AlertasPage() {
  const { getSSTAlertas, isLoading } = useMiNegocioApi();
  const [alerts, setAlerts] = useState<any[]>([]);

  useEffect(() => {
    getSSTAlertas().then(res => res && setAlerts(res));
  }, [getSSTAlertas]);

  return (
    <div className="space-y-10 animate-in slide-in-from-right-4 duration-500">
      <div className="flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 className="text-3xl font-black uppercase italic text-slate-900 dark:text-white leading-none mb-3">Centro de Alertas</h1>
          <p className="text-slate-500 font-medium">Monitoreo en tiempo real de desviaciones normativas y eventos de alto impacto.</p>
        </div>
        <div className="flex gap-3">
           <Button variant="ghost" className="font-bold text-slate-500 hover:text-red-600 transition-colors">
              <FiTrash2 className="mr-2" /> Limpiar Historial
           </Button>
           <Button className="bg-slate-900 text-white font-black px-8 h-14 rounded-2xl shadow-xl transition-all">
              Configurar Notificaciones
           </Button>
        </div>
      </div>

      <div className="space-y-6">
        {alerts.map((a, i) => (
          <Card key={i} className={`border-none shadow-sm p-10 rounded-[2.5rem] transition-all relative overflow-hidden group ${a.leida ? 'opacity-50 bg-slate-50 dark:bg-black/10' : 'bg-white dark:bg-brand-deep/10 ring-1 ring-slate-100 dark:ring-white/5'}`}>
             {!a.leida && a.criticidad === 'CRITICA' && (
                <div className="absolute left-0 top-0 bottom-0 w-2 bg-red-600 shadow-[0_0_15px_rgba(220,38,38,0.5)]" />
             )}

             <div className="flex flex-col md:flex-row justify-between gap-10">
                <div className="flex gap-8 flex-1">
                   <div className={`p-6 rounded-3xl h-fit shadow-inner ${
                      a.criticidad === 'CRITICA' ? 'bg-red-50 text-red-600 dark:bg-red-900/20' :
                      a.criticidad === 'ALTA' ? 'bg-orange-50 text-orange-600 dark:bg-orange-900/20' :
                      'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/20'
                   }`}>
                      <FiAlertCircle size={32} />
                   </div>
                   <div className="space-y-3 flex-1">
                      <div className="flex items-center gap-4">
                         <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest font-mono">{new Date(a.fecha_generacion).toLocaleString('es-CO')}</span>
                         <Badge className={`text-[9px] font-black px-3 py-1 rounded-lg ${
                            a.criticidad === 'CRITICA' ? 'bg-red-600 text-white' :
                            a.criticidad === 'ALTA' ? 'bg-orange-500 text-white' :
                            'bg-indigo-600 text-white'
                         }`}>{a.criticidad}</Badge>
                      </div>
                      <h3 className="text-2xl font-black text-slate-800 dark:text-white tracking-tight leading-tight">{a.titulo}</h3>
                      <p className="text-lg text-slate-600 dark:text-slate-400 font-medium leading-relaxed max-w-4xl">{a.mensaje}</p>
                   </div>
                </div>

                <div className="flex flex-row md:flex-col justify-end gap-3 shrink-0">
                   {!a.leida ? (
                      <Button className="bg-emerald-500 hover:bg-emerald-600 text-white font-black uppercase text-[10px] tracking-widest px-8 py-4 rounded-xl shadow-lg shadow-emerald-500/20">
                         <FiCheck className="mr-2" size={16} /> Resolver
                      </Button>
                   ) : (
                      <Badge variant="outline" className="w-fit self-end font-bold px-4 py-2 border-slate-200">PROCESADA</Badge>
                   )}
                   <Button variant="ghost" className="text-slate-400 font-bold uppercase text-[10px] tracking-widest hover:text-brand">Detalles Técnicos</Button>
                </div>
             </div>
          </Card>
        ))}

        {alerts.length === 0 && !isLoading && (
          <div className="p-40 text-center border-2 border-dashed border-slate-200 dark:border-white/5 rounded-[4rem] bg-white/30 dark:bg-transparent">
             <div className="relative inline-block mb-8">
                <FiBell size={80} className="text-slate-200 dark:text-slate-800" />
                <div className="absolute top-0 right-0 w-6 h-6 bg-emerald-500 rounded-full border-4 border-white dark:border-brand-deep shadow-sm" />
             </div>
             <p className="text-slate-400 text-xl font-black uppercase italic tracking-widest">Canal de Alerta Despejado</p>
             <p className="text-slate-400 text-sm mt-3 max-w-xs mx-auto font-medium">El sistema de gobernanza no reporta incidencias críticas pendientes de revisión.</p>
          </div>
        )}
      </div>

      {!isLoading && alerts.length > 0 && (
         <div className="flex justify-center pt-10">
            <Button variant="outline" className="rounded-full px-12 py-6 font-black uppercase text-xs tracking-[0.2em] border-slate-200 hover:bg-slate-50 transition-all">Cargar Histórico Anterior</Button>
         </div>
      )}
    </div>
  );
}
