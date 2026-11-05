'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import {
  FiClock, FiAward, FiUsers, FiShield, FiFileText, FiLink, FiAlertOctagon, FiRotateCcw
} from 'react-icons/fi';
import { ViewState } from '@/components/ui/ViewState';
import { CriticalActionDialog } from '@/components/ui/CriticalActionDialog';
import { toast } from 'react-hot-toast';

export default function MemoriaHistoricaPage() {
  const [isLoading] = useState(false);
  const [isHandoverOpen, setIsHandoverOpen] = useState(false);

  const milestones = [
    {
        date: '2024-03-15',
        event: 'Despliegue Nodo Nacional',
        description: 'Inicio de la red soberana Sarita. Definición del Kernel Génesis.',
        hash: '0000a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6'
    },
    {
        date: '2024-04-02',
        event: 'Institucionalización Fase 8',
        description: 'Normalización de lenguaje y certificación de IA como Funcionario Digital.',
        hash: 'b7a3f2...9c4d1e'
    },
    {
        date: '2024-05-10',
        event: 'Escalamiento Fase 9',
        description: 'Federación de nodos territoriales. Activación de Kill Switches jerárquicos.',
        hash: 'e8d1c0...2f5a6b'
    }
  ];

  const handoverProtocols = [
    { name: 'Protocolo de Transición Administrativa', status: 'READY', desc: 'Prepara el bundle de evidencia para nueva autoridad.' },
    { name: 'Custodia de Secretos Jurisdiccionales', status: 'LOCKED', desc: 'Transferencia de llaves de cifrado de nodo.' },
    { name: 'Declaración de Permanencia Histórica', status: 'ACTIVE', desc: 'Asegura la inmutabilidad de los registros previos.' }
  ];

  const handleHandover = () => {
    setIsHandoverOpen(true);
  };

  const confirmHandover = () => {
    toast.success("PROTOCOLO DE TRANSICIÓN INICIADO. Generando bitácora de entrega inmutable...");
    setTimeout(() => toast.success("EXPEDIENTE DE TRASPASO (CERTIFICADO) DISPONIBLE."), 2000);
    setIsHandoverOpen(false);
  };

  return (
    <ViewState isLoading={isLoading}>
      <div className="space-y-10 animate-in fade-in duration-700">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-gray-100 pb-8">
            <div>
                <div className="flex items-center gap-3 mb-2">
                    <div className="bg-slate-900 text-white p-2 rounded-lg">
                        <FiClock size={24} />
                    </div>
                    <h1 className="text-4xl font-black text-slate-900 tracking-tighter uppercase italic">Memoria Histórica y Permanencia</h1>
                </div>
                <p className="text-slate-500 text-lg font-medium italic">Garantía de irreversibilidad estratégica y trazabilidad generacional.</p>
            </div>
            <Button
                onClick={handleHandover}
                className="bg-indigo-600 text-white font-black px-8 py-6 rounded-2xl flex items-center gap-2 uppercase tracking-widest text-xs shadow-lg shadow-indigo-500/20"
            >
                <FiUsers /> Iniciar Traspaso Institucional
            </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-6">
                <h3 className="text-xl font-black text-slate-900 uppercase tracking-widest flex items-center gap-2 italic">
                    <FiAward className="text-brand" /> Hitos de Evolución del Sistema
                </h3>
                <div className="relative border-l-2 border-slate-100 ml-4 pl-8 space-y-12 py-4">
                    {milestones.map((m, i) => (
                        <div key={i} className="relative">
                            <div className="absolute -left-[41px] top-0 w-5 h-5 rounded-full bg-white border-4 border-brand shadow-sm" />
                            <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-50 hover:border-brand/20 transition-all">
                                <div className="flex justify-between items-start mb-4">
                                    <span className="text-xs font-black text-indigo-500 uppercase tracking-widest">{m.date}</span>
                                    <Badge variant="outline" className="font-mono text-[8px] text-slate-400">HASH: {m.hash.substring(0,16)}...</Badge>
                                </div>
                                <h4 className="text-2xl font-black text-slate-900 uppercase italic mb-2">{m.event}</h4>
                                <p className="text-slate-500 leading-relaxed italic">"{m.description}"</p>
                                <div className="mt-6 pt-6 border-t border-slate-50 flex gap-4">
                                    <Button variant="ghost" size="sm" className="text-[10px] font-black uppercase tracking-widest text-indigo-600"><FiFileText className="mr-2" /> Ver Evidencia</Button>
                                    <Button variant="ghost" size="sm" className="text-[10px] font-black uppercase tracking-widest text-slate-400"><FiLink className="mr-2" /> Certificar Integridad</Button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="space-y-8">
                <div>
                    <h3 className="text-xl font-black text-slate-900 uppercase tracking-widest flex items-center gap-2 italic mb-6">
                        <FiShield className="text-emerald-500" /> Blindaje Institucional
                    </h3>
                    <div className="space-y-4">
                        {handoverProtocols.map((p, i) => (
                            <Card key={i} className="border-none shadow-sm bg-white overflow-hidden rounded-2xl group">
                                <div className="p-6">
                                    <div className="flex justify-between items-start mb-2">
                                        <h4 className="text-sm font-black text-slate-900 uppercase leading-tight">{p.name}</h4>
                                        <Badge className={p.status === 'READY' ? 'bg-emerald-500' : p.status === 'LOCKED' ? 'bg-slate-900' : 'bg-brand'}>
                                            {p.status}
                                        </Badge>
                                    </div>
                                    <p className="text-xs text-slate-400">{p.desc}</p>
                                </div>
                            </Card>
                        ))}
                    </div>
                </div>

                <Card className="bg-slate-900 text-white p-8 rounded-[2.5rem] relative overflow-hidden">
                    <div className="absolute -right-10 -bottom-10 opacity-10">
                        <FiAlertOctagon size={200} />
                    </div>
                    <div className="relative z-10">
                        <p className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.3em] mb-4">Mecanismo Anti-Borrado</p>
                        <h4 className="text-xl font-black italic mb-4">Irreversibilidad del Rastro</h4>
                        <p className="text-xs text-slate-400 leading-relaxed mb-6">
                            El Kernel Sarita impide la eliminación física de cualquier evento de gobernanza. La historia del sistema es acumulativa y auditable por periodos de 20 años.
                        </p>
                        <div className="flex items-center gap-2 text-emerald-400 font-black text-[10px] uppercase">
                            <FiShield /> Protección de Datos Generacional
                        </div>
                    </div>
                </Card>
            </div>
        </div>

        <CriticalActionDialog
            isOpen={isHandoverOpen}
            onClose={() => setIsHandoverOpen(false)}
            onConfirm={confirmHandover}
            title="PROTOCOLARIZACIÓN DE TRASPASO INSTITUCIONAL"
            description="Se procederá a la consolidación de toda la bitácora de soberanía, configuraciones del kernel y evidencias de auditoría para la transferencia de autoridad. Este proceso es inalterable y genera una 'cicatriz digital' que vincula a la administración actual con los resultados obtenidos. ¿Desea ejecutar el cierre de periodo?"
            confirmLabel="PROTOCOLARIZAR ENTREGA"
            type="sovereign"
        />
      </div>
    </ViewState>
  );
}
