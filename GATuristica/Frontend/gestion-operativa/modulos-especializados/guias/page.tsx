'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  FiMap,
  FiPlus,
  FiCalendar,
  FiUsers,
  FiActivity,
  FiMapPin,
  FiClock,
  FiChevronRight
} from 'react-icons/fi';
import { Badge } from '@/components/ui/Badge';

export default function GuideManagementPage() {
  const { getTours, isLoading } = useMiNegocioApi();
  const [activeTours, setActiveTours] = useState<any[]>([]);

  useEffect(() => {
    const loadData = async () => {
      const data = await getTours();
      if (data) setActiveTours(data.results || []);
    };
    loadData();
  }, [getTours]);

  return (
    <div className="space-y-10 animate-in slide-in-from-right-8 duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight uppercase italic leading-none mb-2">Despliegue de Experiencias y Tours</h1>
          <p className="text-slate-500 dark:text-slate-400 text-lg">Diseño de itinerarios, asignación de guías y control de expediciones.</p>
        </div>
        <Button className="bg-brand text-white font-black px-8 py-6 rounded-2xl shadow-xl shadow-brand/20">
           <FiPlus className="mr-2" /> Crear Experiencia
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
         <Card className="lg:col-span-2 border-none shadow-sm bg-white dark:bg-brand-deep/10 overflow-hidden rounded-[2rem]">
            <CardHeader className="p-10 border-b border-slate-50 dark:border-white/5 flex flex-row items-center justify-between">
               <CardTitle className="text-2xl font-black italic flex items-center gap-3 text-brand">
                  <FiMap /> Itinerarios Activos
               </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
               <div className="divide-y divide-slate-50 dark:divide-white/5">
                  {activeTours.map((tour, i) => (
                    <div key={i} className="p-10 hover:bg-slate-50 dark:hover:bg-white/5 transition-all group flex flex-col md:flex-row md:items-center justify-between gap-8">
                       <div className="flex items-center gap-8">
                          <div className="w-20 h-20 bg-slate-900 rounded-3xl flex items-center justify-center text-white group-hover:bg-brand transition-colors duration-500 shadow-2xl">
                             <FiMapPin size={32} />
                          </div>
                          <div>
                             <h4 className="text-2xl font-black text-slate-900 dark:text-white uppercase tracking-tighter mb-2 italic">{tour.product?.nombre || tour.nombre}</h4>
                             <div className="flex items-center gap-6 text-xs font-bold text-slate-400 uppercase tracking-widest">
                                <span className="flex items-center gap-1.5"><FiClock className="text-brand" /> {tour.duracion_horas || 'N/A'}h</span>
                                <span className="flex items-center gap-1.5"><FiUsers className="text-brand" /> {tour.nivel_dificultad || 'Bajo'}</span>
                             </div>
                          </div>
                       </div>
                       <div className="flex items-center gap-10">
                          <div className="text-right">
                             <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Precio Unitario</p>
                             <p className="text-2xl font-black text-slate-900 dark:text-white">${tour.product?.base_price || '0'}</p>
                          </div>
                          <Button variant="ghost" className="h-14 w-14 rounded-2xl bg-slate-50 dark:bg-black/20 text-slate-400 hover:text-brand hover:bg-brand/10 transition-all">
                             <FiChevronRight size={24} />
                          </Button>
                       </div>
                    </div>
                  ))}
                  {activeTours.length === 0 && !isLoading && (
                    <div className="p-20 text-center text-slate-400 italic">
                       No hay experiencias configuradas en el catálogo.
                    </div>
                  )}
               </div>
            </CardContent>
         </Card>

         <div className="space-y-8">
            <Card className="border-none shadow-xl bg-slate-900 text-white p-10 rounded-[2.5rem] relative overflow-hidden group">
               <div className="absolute -right-6 -bottom-6 opacity-20 group-hover:scale-110 transition-transform duration-700">
                  <FiActivity size={180} />
               </div>
               <p className="text-[10px] font-black uppercase tracking-widest text-brand-light mb-6">Analítica de Rutas</p>
               <h3 className="text-3xl font-black italic leading-tight">La ruta "Rio Meta" es tendencia esta semana.</h3>
               <p className="mt-6 text-sm text-slate-400 font-medium">SADI recomienda habilitar 2 guías adicionales para el sábado.</p>
               <Button className="w-full mt-10 bg-brand hover:bg-brand-light font-black py-4 rounded-xl shadow-2xl">Audit Capacity</Button>
            </Card>

            <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-10 rounded-[2.5rem]">
               <h4 className="text-xl font-black text-slate-900 dark:text-white mb-8">Disponibilidad de Guías</h4>
               <div className="space-y-6">
                  {[1, 2].map(i => (
                    <div key={i} className="flex items-center gap-4 p-4 bg-slate-50 dark:bg-black/20 rounded-2xl">
                       <div className="w-10 h-10 rounded-full bg-brand/20 flex items-center justify-center font-black text-brand text-xs">GP</div>
                       <div className="flex-1">
                          <p className="text-sm font-bold text-slate-800 dark:text-slate-200">Guía Profesional {i}</p>
                          <Badge className="bg-emerald-100 text-emerald-700 border-none font-black text-[8px] px-2">ONLINE</Badge>
                       </div>
                    </div>
                  ))}
               </div>
            </Card>
         </div>
      </div>
    </div>
  );
}
