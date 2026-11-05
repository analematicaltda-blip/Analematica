'use client';

import React, { useEffect, useState } from 'react';
import {
  getStrategyProposals,
  approveStrategyProposal,
  executeStrategyProposal,
  rejectStrategyProposal,
  StrategyProposal
} from '@/services/intelligence';
import { toast } from 'react-hot-toast';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import {
  FiActivity,
  FiZap,
  FiShield,
  FiCheckCircle,
  FiXCircle,
  FiCpu,
  FiTrendingUp,
  FiAlertTriangle
} from 'react-icons/fi';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

export default function InteligenciaPage() {
  const [proposals, setProposals] = useState<StrategyProposal[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchProposals = async () => {
    try {
      const data = await getStrategyProposals();
      setProposals(data);
    } catch (error) {
      // toast.error("Error al cargar propuestas de inteligencia.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProposals();
  }, []);

  const handleApprove = async (id: string) => {
    try {
      await approveStrategyProposal(id);
      toast.success("Propuesta aprobada.");
      fetchProposals();
    } catch (error) {
      toast.error("Error al aprobar.");
    }
  };

  const handleExecute = async (id: string) => {
    try {
      await executeStrategyProposal(id);
      toast.success("Acción ejecutada correctamente.");
      fetchProposals();
    } catch (error) {
      toast.error("Error en la ejecución.");
    }
  };

  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      {/* Strategic Header */}
      <div className="bg-slate-900 rounded-[2.5rem] p-12 text-white shadow-2xl relative overflow-hidden">
         <div className="absolute top-0 right-0 p-16 opacity-5">
            <FiCpu size={350} />
         </div>
         <div className="relative z-10">
            <div className="inline-flex items-center gap-2 bg-indigo-500/20 border border-indigo-400/30 px-4 py-2 rounded-full mb-8">
               <div className="w-2 h-2 bg-indigo-400 rounded-full animate-pulse" />
               <span className="text-[10px] font-black uppercase tracking-widest text-indigo-300">Strategic Decision Core</span>
            </div>
            <h1 className="text-6xl font-black tracking-tighter mb-6 uppercase leading-tight max-w-4xl">Núcleo de Inteligencia Estratégica</h1>
            <p className="text-xl text-slate-400 leading-relaxed max-w-2xl font-medium">
               Análisis sensorial del ecosistema en tiempo real. Los funcionarios digitales proponen mandatos operativos de alta escala para garantizar la soberanía económica.
            </p>
         </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
         {/* Main Proposal Feed */}
         <div className="lg:col-span-2 space-y-6">
            <h2 className="text-xl font-black text-slate-900 dark:text-white uppercase tracking-widest flex items-center gap-3">
               <FiActivity className="text-brand" /> Feed de Recomendaciones
            </h2>

            {loading ? (
               <div className="space-y-6">
                  {[...Array(2)].map((_, i) => <div key={i} className="h-64 bg-white dark:bg-brand-deep/10 rounded-3xl animate-pulse" />)}
               </div>
            ) : (
               <div className="space-y-6">
                  {proposals.map((proposal) => (
                    <Card key={proposal.id} className="border-none shadow-sm bg-white dark:bg-brand-deep/20 rounded-3xl overflow-hidden hover:shadow-xl transition-all duration-500 group">
                       <CardContent className="p-10">
                          <div className="flex justify-between items-start mb-8">
                             <div className="flex items-center gap-4">
                                <div className="w-12 h-12 bg-indigo-50 dark:bg-brand-deep/40 rounded-2xl flex items-center justify-center text-indigo-600">
                                   <FiShield size={24} />
                                </div>
                                <div>
                                   <Badge className="bg-indigo-100 text-indigo-700 border-none font-black text-[9px] px-3 py-1 mb-1">{proposal.domain}</Badge>
                                   <h3 className="text-2xl font-black text-slate-900 dark:text-white tracking-tighter uppercase">{proposal.accion_sugerida.intention.replace('PLATFORM_', '')}</h3>
                                </div>
                             </div>
                             <div className="text-right">
                                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Nivel de Decisión</p>
                                <p className="text-lg font-black text-indigo-600 italic">
                                   {proposal.decision_level === 1 ? 'Automática' : proposal.decision_level === 2 ? 'Supervisada' : 'Estratégica'}
                                </p>
                             </div>
                          </div>

                          <div className="grid md:grid-cols-2 gap-8 mb-10">
                             <div className="bg-slate-50 dark:bg-black/20 p-6 rounded-2xl border border-slate-100 dark:border-white/5">
                                <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3">Contexto Detectado</h4>
                                <p className="text-sm font-bold text-slate-700 dark:text-slate-200 leading-relaxed italic">"{proposal.contexto_detectado}"</p>
                             </div>
                             <div className="bg-slate-50 dark:bg-black/20 p-6 rounded-2xl border border-slate-100 dark:border-white/5">
                                <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3">Riesgo Actual</h4>
                                <p className="text-sm font-bold text-red-600 leading-relaxed italic">"{proposal.riesgo_actual}"</p>
                             </div>
                          </div>

                          <div className="flex items-center justify-between pt-8 border-t border-slate-50 dark:border-white/5">
                             <div className="flex gap-2">
                                {proposal.status === 'PENDING' && (
                                   <>
                                      <Button
                                        onClick={() => handleApprove(proposal.id)}
                                        className="bg-emerald-600 hover:bg-emerald-700 text-white font-black px-8 py-6 rounded-2xl shadow-lg shadow-emerald-600/20"
                                      >
                                        <FiCheckCircle className="mr-2" /> Autorizar
                                      </Button>
                                      <Button
                                        variant="ghost"
                                        onClick={() => rejectStrategyProposal(proposal.id).then(() => fetchProposals())}
                                        className="text-slate-400 hover:text-red-500 font-bold"
                                      >
                                        Descartar
                                      </Button>
                                   </>
                                )}
                                {proposal.status === 'APPROVED' && (
                                   <Button
                                     onClick={() => handleExecute(proposal.id)}
                                     className="bg-brand hover:bg-brand-light text-white font-black px-10 py-6 rounded-2xl"
                                   >
                                     <FiZap className="mr-2" /> Ejecutar Ahora
                                   </Button>
                                )}
                                {proposal.status === 'EXECUTED' && (
                                   <div className="flex items-center gap-2 text-emerald-600 font-black italic">
                                      <FiCheckCircle /> OPERACIÓN COMPLETADA
                                   </div>
                                )}
                             </div>
                             <Badge variant="outline" className="opacity-40">{proposal.id}</Badge>
                          </div>
                       </CardContent>
                    </Card>
                  ))}

                  {proposals.length === 0 && (
                    <div className="text-center py-32 bg-white dark:bg-brand-deep/5 rounded-[3rem] border-2 border-dashed border-slate-100 dark:border-white/5">
                       <FiShield size={64} className="mx-auto text-slate-200 mb-6" />
                       <h3 className="text-xl font-black text-slate-400 uppercase tracking-widest">Estado Nominal Alcanzado</h3>
                       <p className="text-slate-500 mt-2">No hay intervenciones críticas requeridas por el momento.</p>
                    </div>
                  )}
               </div>
            )}
         </div>

         {/* Decision Analytics Panel */}
         <div className="space-y-8">
            <Card className="border-none shadow-xl bg-indigo-600 text-white p-10 rounded-[2.5rem] overflow-hidden relative">
               <div className="absolute -right-6 -bottom-6 opacity-20 group-hover:scale-110 transition-transform duration-700">
                  <FiTrendingUp size={180} />
               </div>
               <p className="text-xs font-black uppercase tracking-widest text-indigo-200 mb-4">Soberanía Aplicada</p>
               <h3 className="text-5xl font-black italic tracking-tighter">98.2%</h3>
               <p className="mt-8 text-sm leading-relaxed text-indigo-100 font-medium">Tasa de acierto en las últimas 50 decisiones estratégicas supervisadas.</p>
            </Card>

            <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-10 rounded-[2.5rem]">
               <h3 className="text-xl font-black text-slate-900 dark:text-white mb-8">Cuerpo de Funcionarios Digitales</h3>
               <div className="space-y-8">
                  <div className="flex items-center justify-between">
                     <div className="flex items-center gap-4">
                        <div className="w-10 h-10 bg-emerald-50 text-emerald-600 rounded-xl flex items-center justify-center font-black">M</div>
                        <span className="text-sm font-bold text-slate-600 dark:text-slate-400">Especialista de Marketing</span>
                     </div>
                     <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                  </div>
                  <div className="flex items-center justify-between">
                     <div className="flex items-center gap-4">
                        <div className="w-10 h-10 bg-indigo-50 text-indigo-600 rounded-xl flex items-center justify-center font-black">F</div>
                        <span className="text-sm font-bold text-slate-600 dark:text-slate-400">Auditor Financiero Digital</span>
                     </div>
                     <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                  </div>
                  <div className="flex items-center justify-between">
                     <div className="flex items-center gap-4">
                        <div className="w-10 h-10 bg-slate-100 text-slate-400 rounded-xl flex items-center justify-center font-black italic">G</div>
                        <span className="text-sm font-bold text-slate-400">Centinela de Gobernanza</span>
                     </div>
                     <Badge variant="outline" className="text-[8px] opacity-50">ESPERA</Badge>
                  </div>
               </div>
            </Card>

            <div className="p-10 bg-amber-50 dark:bg-amber-900/10 rounded-[2.5rem] border border-amber-100 dark:border-amber-900/20">
               <FiAlertTriangle className="text-amber-600 mb-4" size={32} />
               <h4 className="font-black text-amber-900 dark:text-amber-400 uppercase tracking-widest text-xs mb-2">Protocolo de Emergencia</h4>
               <p className="text-xs text-amber-700 dark:text-amber-500 leading-relaxed">Solo la Autoridad Soberana puede realizar intervenciones manuales que omitan las políticas del Kernel.</p>
               <Button className="w-full mt-6 bg-amber-600 hover:bg-amber-700 text-white font-black py-4 rounded-xl shadow-lg shadow-amber-600/20">
                  Activar Override
               </Button>
            </div>
         </div>
      </div>
    </div>
  );
}
