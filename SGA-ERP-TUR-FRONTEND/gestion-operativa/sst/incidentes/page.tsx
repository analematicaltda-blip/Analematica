'use client';
import React, { useEffect, useState } from 'react';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { FiPlus, FiFileText, FiSearch, FiClock } from 'react-icons/fi';

export default function IncidentesPage() {
  const { getSSTIncidents, isLoading } = useMiNegocioApi();
  const [incidents, setIncidents] = useState<any[]>([]);

  useEffect(() => {
    getSSTIncidents().then(res => res && setIncidents(res));
  }, [getSSTIncidents]);

  return (
    <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 className="text-3xl font-black uppercase italic text-slate-900 dark:text-white leading-tight">Incidentes y Accidentes</h1>
          <p className="text-slate-500">Reporte, investigación y seguimiento de eventos laborales bajo normativa legal.</p>
        </div>
        <Button className="bg-red-600 hover:bg-red-700 text-white font-black px-8 h-14 rounded-2xl shadow-xl shadow-red-600/20 transition-all scale-100 hover:scale-105 active:scale-95">
          <FiPlus className="mr-2" /> Reportar Nuevo Evento
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-4">
          {incidents.map((inc, i) => (
            <Card key={i} className="border-none shadow-sm hover:shadow-md transition-all overflow-hidden group bg-white dark:bg-brand-deep/10">
              <div className="flex">
                <div className={`w-2 ${inc.tipo === 'ACCIDENTE' ? 'bg-red-600' : 'bg-amber-500'}`} />
                <div className="p-8 flex-1 flex flex-col md:flex-row justify-between gap-6">
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{new Date(inc.fecha_hora).toLocaleString()}</span>
                      <Badge variant="outline" className="text-[10px] font-black">{inc.tipo}</Badge>
                      <Badge className={inc.gravedad === 'MORTAL' ? 'bg-black text-white' : inc.gravedad === 'GRAVE' ? 'bg-red-600 text-white' : 'bg-amber-500 text-white'}>{inc.gravedad}</Badge>
                    </div>
                    <h3 className="text-xl font-bold text-slate-800 dark:text-white group-hover:text-brand transition-colors">{inc.descripcion_hechos}</h3>
                    <p className="text-slate-500 text-sm flex items-center gap-2 italic">
                      <FiSearch /> Lugar: {inc.lugar}
                    </p>
                  </div>
                  <div className="flex flex-col items-end justify-between">
                     <Badge className={inc.estado_investigacion === 'CERRADA' ? 'bg-emerald-100 text-emerald-700' : 'bg-blue-100 text-blue-700'}>
                        {inc.estado_investigacion}
                     </Badge>
                     <Button variant="ghost" className="text-xs font-black uppercase tracking-widest text-brand p-0 h-auto">Ver Investigación →</Button>
                  </div>
                </div>
              </div>
            </Card>
          ))}
          {incidents.length === 0 && !isLoading && (
            <div className="p-20 text-center border-2 border-dashed border-slate-200 dark:border-white/5 rounded-3xl text-slate-400 italic">
              <FiFileText className="mx-auto mb-4 opacity-20" size={48} />
              No se registran eventos laborales en el sistema.
            </div>
          )}
        </div>

        <div className="space-y-8">
           <Card className="border-none shadow-sm bg-slate-900 text-white p-8">
              <CardTitle className="text-lg font-black uppercase mb-6 flex items-center gap-2">
                 <FiClock className="text-brand-light" /> Tiempos de Respuesta
              </CardTitle>
              <div className="space-y-6">
                 <div>
                    <p className="text-[10px] font-black text-slate-400 uppercase mb-1 font-mono">Promedio Apertura Investigación</p>
                    <p className="text-2xl font-black text-brand-light font-mono">1.2 HORAS</p>
                 </div>
                 <div className="h-px bg-white/5" />
                 <div>
                    <p className="text-[10px] font-black text-slate-400 uppercase mb-1 font-mono">Cierre de Plan de Acción</p>
                    <p className="text-2xl font-black text-emerald-400 font-mono">4.5 DÍAS</p>
                 </div>
              </div>
           </Card>

           <Card className="border-none shadow-sm p-8 bg-white dark:bg-brand-deep/10">
              <h4 className="font-bold mb-4 flex items-center gap-2">
                 <FiFileText className="text-indigo-600" /> Integridad Legal
              </h4>
              <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed mb-6">Todos los reportes están vinculados a la bitácora inmutable de agentes SARITA. Los registros cuentan con firma digital y marca de tiempo Blockchain.</p>
              <Button variant="outline" className="w-full font-bold text-xs uppercase tracking-widest border-slate-200">Verificar Evidencias</Button>
           </Card>
        </div>
      </div>
    </div>
  );
}
