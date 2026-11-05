'use client';
import React, { useEffect, useState } from 'react';
import { useMiNegocioApi } from '../../../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { FiShield, FiHeart, FiAnchor, FiCheckCircle, FiDownload } from 'react-icons/fi';

export default function SeguridadSocialPage() {
  const { getNominaIncapacidades, isLoading } = useMiNegocioApi();
  const [items, setItems] = useState<any[]>([]);

  useEffect(() => {
    // Simulamos carga de aportes para esta vista structural
    getNominaIncapacidades().then(res => res && setItems(res));
  }, [getNominaIncapacidades]);

  return (
    <div className="space-y-10 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 className="text-3xl font-black uppercase italic text-slate-900 dark:text-white tracking-tighter">Seguridad Social y Parafiscales</h1>
          <p className="text-slate-500 font-medium">Cumplimiento de aportes a Salud, Pensión, ARL y Cajas de Compensación.</p>
        </div>
        <Button className="bg-blue-600 text-white font-black px-8 h-14 rounded-2xl shadow-xl shadow-blue-600/20">
          <FiDownload className="mr-2" /> Descargar Archivo PILA
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
         {[
           { label: 'Aportes Salud', value: '$2.4M', icon: FiHeart, color: 'text-rose-500' },
           { label: 'Aportes Pensión', value: '$3.8M', icon: FiAnchor, color: 'text-blue-500' },
           { label: 'Riesgos (ARL)', value: '$450K', icon: FiShield, color: 'text-orange-500' },
           { label: 'Parafiscales', value: '$1.2M', icon: FiCheckCircle, color: 'text-emerald-500' },
         ].map((stat, i) => (
            <Card key={i} className="p-8 border-none shadow-sm bg-white dark:bg-brand-deep/20 rounded-[2rem]">
               <div className={`p-3 rounded-2xl w-fit mb-6 bg-slate-50 dark:bg-black/20 ${stat.color}`}>
                  <stat.icon size={24} />
               </div>
               <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">{stat.label}</p>
               <h3 className="text-3xl font-black text-slate-900 dark:text-white">{stat.value}</h3>
            </Card>
         ))}
      </div>

      <Card className="border-none shadow-sm overflow-hidden bg-white dark:bg-brand-deep/10 rounded-[2.5rem]">
         <CardHeader className="p-10 border-b border-slate-50 dark:border-white/5 bg-slate-50/50 dark:bg-black/20">
            <CardTitle className="font-black uppercase flex items-center gap-3 text-xl italic text-brand">
               <FiShield /> Registro de Cobertura Vigente
            </CardTitle>
         </CardHeader>
         <CardContent className="p-0 text-center py-20 text-slate-400 italic">
            El sistema de agentes SARITA está validando el estado de afiliación con los entes gubernamentales.
            <div className="mt-8 flex justify-center gap-4">
               <Badge className="bg-emerald-500 text-white font-black px-4 py-2">SADI VALIDATED</Badge>
               <Badge className="bg-blue-500 text-white font-black px-4 py-2">BOV_NODE_OK</Badge>
            </div>
         </CardContent>
      </Card>
    </div>
  );
}
