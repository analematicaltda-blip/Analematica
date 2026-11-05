'use client';

import React, { useEffect, useState } from 'react';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FiAlertCircle, FiCheckCircle, FiBell, FiShield, FiAlertTriangle } from 'react-icons/fi';
import { Badge } from '@/components/ui/Badge';

export default function AlertasFinancierasPage() {
  const { getAlertas, resolverAlerta, isLoading } = useMiNegocioApi();
  const [data, setData] = useState<any[]>([]);

  const load = async () => {
    const res = await getAlertas();
    if (res) setData(res);
  };

  useEffect(() => { load(); }, [getAlertas]);

  const handleResolve = async (id: string) => {
    await resolverAlerta(id);
    load();
  };

  return (
    <div className="space-y-8 py-8 animate-in slide-in-from-right-4 duration-500 max-w-4xl mx-auto">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-4">
           <div className="w-12 h-12 bg-slate-900 text-white rounded-2xl flex items-center justify-center shadow-lg">
              <FiBell size={24} />
           </div>
           <div>
              <h1 className="text-3xl font-black text-slate-900 tracking-tight">Centro de Alertas de Gobierno</h1>
              <p className="text-slate-500">Notificaciones críticas de integridad y salud financiera.</p>
           </div>
        </div>
        <Button variant="outline" onClick={load} className="font-bold">Sincronizar</Button>
      </div>

      <div className="space-y-4">
        {data.map((a: any) => (
          <Card key={a.id} className={`border-none shadow-sm transition-all ${a.resuelta ? 'opacity-50' : 'hover:shadow-md'}`}>
            <CardContent className="p-0">
               <div className="flex items-stretch min-h-[120px]">
                  <div className={`w-2 ${a.resuelta ? 'bg-slate-200' : a.nivel_prioridad === 'CRITICA' ? 'bg-red-500' : 'bg-amber-500'}`} />
                  <div className="flex-1 p-6 flex items-center justify-between gap-8">
                     <div className="flex gap-6 items-start">
                        <div className={`mt-1 ${a.resuelta ? 'text-slate-300' : a.nivel_prioridad === 'CRITICA' ? 'text-red-500' : 'text-amber-500'}`}>
                           {a.resuelta ? <FiCheckCircle size={28} /> : <FiAlertTriangle size={28} />}
                        </div>
                        <div className="space-y-1">
                           <div className="flex items-center gap-2">
                              <Badge variant="outline" className="text-[8px] font-black uppercase tracking-tighter border-slate-100">
                                 {a.tipo.replace(/_/g, ' ')}
                              </Badge>
                              {!a.resuelta && (
                                 <span className="animate-pulse w-2 h-2 rounded-full bg-red-500" />
                              )}
                           </div>
                           <h3 className="text-lg font-bold text-slate-800">{a.titulo}</h3>
                           <p className="text-sm text-slate-500 leading-relaxed">{a.descripcion}</p>
                           <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest pt-2">Detectado: {new Date(a.fecha_creacion).toLocaleString()}</p>
                        </div>
                     </div>
                     {!a.resuelta && (
                        <Button
                           onClick={() => handleResolve(a.id)}
                           className="bg-slate-900 text-white font-bold text-xs uppercase px-6"
                        >
                           Marcar Resuelta
                        </Button>
                     )}
                  </div>
               </div>
            </CardContent>
          </Card>
        ))}

        {data.length === 0 && (
           <div className="py-32 text-center bg-white rounded-3xl border border-slate-100 flex flex-col items-center">
              <FiShield size={48} className="text-green-500 mb-4 opacity-20" />
              <p className="text-lg font-black text-slate-400 uppercase tracking-tighter">Sin alertas activas</p>
              <p className="text-sm text-slate-400">El sistema se encuentra en un estado íntegro y estable.</p>
           </div>
        )}
      </div>
    </div>
  );
}
