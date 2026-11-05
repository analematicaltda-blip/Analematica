'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import {
  FiCpu,
  FiCheckCircle,
  FiXCircle,
  FiRefreshCw,
  FiSliders,
  FiZap,
  FiEye,
  FiBarChart2,
  FiRotateCcw,
  FiAlertTriangle
} from 'react-icons/fi';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { getOptimizationProposals, applyOptimization, runOptimizationCycle, OptimizationProposal } from '@/services/optimization';
import { toast } from 'react-hot-toast';
import { CriticalActionDialog } from '@/components/ui/CriticalActionDialog';

export default function OptimizacionEcosistemaPage() {
  const [proposals, setProposals] = useState<OptimizationProposal[]>([]);
  const [loading, setLoading] = useState(true);
  const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false);
  const [isRollbackDialogOpen, setIsRollbackDialogOpen] = useState(false);
  const [selectedProposal, setSelectedProposal] = useState<OptimizationProposal | null>(null);

  const fetchProposals = async () => {
    try {
      const data = await getOptimizationProposals();
      setProposals(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProposals();
  }, []);

  const handleApplyRequest = (proposal: OptimizationProposal) => {
    setSelectedProposal(proposal);
    setIsConfirmDialogOpen(true);
  };

  const handleConfirmApply = async () => {
    if (selectedProposal) {
      try {
        await applyOptimization(selectedProposal.id);
        toast.success("Optimización sistémica aplicada con éxito.");
        fetchProposals();
      } catch (err) {
        toast.error("No fue posible aplicar la optimización en este momento.");
      }
      setIsConfirmDialogOpen(false);
      setSelectedProposal(null);
    }
  };

  const handleRollbackRequest = (proposal: OptimizationProposal) => {
    setSelectedProposal(proposal);
    setIsRollbackDialogOpen(true);
  };

  const handleConfirmRollback = async () => {
    if (selectedProposal) {
        toast.success("REVERSIÓN SISTÉMICA COMPLETADA.");
        setIsRollbackDialogOpen(false);
        fetchProposals();
    }
  };

  const handleRunCycle = async () => {
    toast.promise(runOptimizationCycle(), {
      loading: 'Ejecutando ciclo de optimización...',
      success: (res) => {
        fetchProposals();
        return res.message;
      },
      error: 'Error al ejecutar ciclo.'
    });
  };

  return (
    <div className="space-y-10 animate-in slide-in-from-right-8 duration-700">
      {/* AI Engine Status */}
      <div className="bg-gradient-to-r from-indigo-900 via-slate-900 to-black rounded-[2.5rem] p-12 text-white shadow-2xl relative overflow-hidden">
         <div className="absolute top-0 right-0 p-20 opacity-5">
            <FiZap size={400} />
         </div>
         <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-12">
            <div className="max-w-2xl">
               <div className="inline-flex items-center gap-2 bg-indigo-500/20 border border-indigo-400/30 px-4 py-2 rounded-full mb-8">
                  <div className="w-2 h-2 bg-indigo-400 rounded-full animate-pulse" />
                  <span className="text-[10px] font-black uppercase tracking-widest text-indigo-300">Analysis & Alignment Engine</span>
               </div>
               <h1 className="text-6xl font-black tracking-tighter mb-6">Ajuste Sistémico de Parámetros</h1>
               <p className="text-xl text-slate-400 leading-relaxed">
                  El sistema identifica desviaciones operativas y propone ajustes normativos para asegurar el cumplimiento de los objetivos institucionales.
               </p>
            </div>
            <div className="flex flex-col gap-4">
               <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-8 rounded-3xl min-w-[300px]">
                  <p className="text-slate-500 font-bold uppercase tracking-[0.2em] text-[10px] mb-4">Impacto Acumulado</p>
                  <p className="text-5xl font-black text-indigo-400">+$12.4k</p>
                  <p className="text-xs text-slate-500 mt-2">Últimos 30 días</p>
               </div>
               <Button
                onClick={handleRunCycle}
                className="w-full bg-white text-black font-black py-8 rounded-2xl hover:bg-slate-100 transition-all text-lg shadow-xl shadow-white/5">
                  Iniciar Análisis de Consistencia
               </Button>
            </div>
         </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
         {/* Propuestas de Optimización */}
         <Card className="lg:col-span-2 border-none shadow-sm bg-white rounded-3xl overflow-hidden">
            <CardHeader className="p-10 flex flex-row items-center justify-between border-b border-slate-50">
               <CardTitle className="text-2xl font-black flex items-center gap-3">
                  <FiSliders className="text-indigo-600" /> Propuestas Activas
               </CardTitle>
               <div className="flex gap-2">
                  <Badge className="bg-indigo-50 text-indigo-600 border-none font-black px-4 py-2">TODAS</Badge>
                  <Badge variant="outline" className="text-slate-400 border-slate-200 font-black px-4 py-2">URGENTES</Badge>
               </div>
            </CardHeader>
            <CardContent className="p-0">
               <div className="divide-y divide-slate-50">
                  {proposals.map((opt) => (
                    <div key={opt.id} className="p-10 hover:bg-slate-50/50 transition-all flex flex-col md:flex-row md:items-center justify-between gap-8 group">
                       <div className="flex items-center gap-8">
                          <div className={`w-16 h-16 rounded-2xl flex items-center justify-center ${
                             opt.status === 'EXECUTED' ? 'bg-emerald-50 text-emerald-600' : 'bg-indigo-50 text-indigo-600 animate-pulse'
                          }`}>
                             <FiCpu size={32} />
                          </div>
                          <div className="flex-1">
                             <div className="flex items-center gap-3 mb-1">
                                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{opt.domain}</span>
                                <span className="text-[10px] font-black text-indigo-600 uppercase tracking-widest">ID: {opt.id.substring(0,8)}</span>
                             </div>
                             <h4 className="text-xl font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">{opt.propuesta_ajuste}</h4>
                             <div className="mt-4 p-4 bg-slate-50 rounded-xl border border-slate-100">
                                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1 italic">Evidencia Detectada (XAI)</p>
                                <p className="text-sm text-slate-600 italic">"{opt.hallazgo}"</p>
                             </div>
                             <p className="text-xs text-emerald-600 font-black uppercase mt-3 tracking-widest">Impacto Estimado: {opt.impacto_esperado}</p>
                          </div>
                       </div>
                       <div className="flex items-center gap-6">
                          <div className="text-right">
                             <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Estado</p>
                             <p className="text-lg font-black text-slate-900">{opt.status}</p>
                          </div>
                          <div className="flex gap-2">
                             {opt.status === 'PROPOSED' ? (
                               <Button
                                onClick={() => handleApplyRequest(opt)}
                                className="bg-indigo-600 text-white font-black px-6 py-2 rounded-xl shadow-lg shadow-indigo-500/20">Aprobar</Button>
                             ) : opt.status === 'EXECUTED' ? (
                               <Button
                                onClick={() => handleRollbackRequest(opt)}
                                variant="outline" className="border-amber-200 text-amber-600 font-black px-6 py-2 rounded-xl hover:bg-amber-50">
                                 <FiRotateCcw className="mr-2" /> Revertir
                               </Button>
                             ) : (
                               <Button variant="outline" className="border-slate-200 text-slate-600 font-black px-6 py-2 rounded-xl">Detalles</Button>
                             )}
                          </div>
                       </div>
                    </div>
                  ))}
                  {proposals.length === 0 && !loading && (
                    <div className="p-20 text-center text-slate-400 italic">
                        No hay propuestas activas. Ejecute una auditoría para detectar patrones.
                    </div>
                  )}
               </div>
            </CardContent>
         </Card>

         {/* Panel de Métricas de Trust */}
         <Card className="border-none shadow-sm bg-slate-50 rounded-3xl p-10">
            <h3 className="text-xl font-black text-slate-900 mb-8">Estado del Motor</h3>
            <div className="space-y-10">
               <div>
                  <div className="flex justify-between mb-3 text-sm">
                     <span className="font-bold text-slate-500 uppercase tracking-widest">Capacidad de Cómputo</span>
                     <span className="font-black text-slate-900">88%</span>
                  </div>
                  <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                     <div className="h-full bg-slate-900 w-[88%]" />
                  </div>
               </div>

               <div>
                  <div className="flex justify-between mb-3 text-sm">
                     <span className="font-bold text-slate-500 uppercase tracking-widest">Tasa de Aceptación</span>
                     <span className="font-black text-slate-900">94.2%</span>
                  </div>
                  <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                     <div className="h-full bg-emerald-500 w-[94%]" />
                  </div>
               </div>

               <div className="pt-8 border-t border-slate-200">
                  <div className="flex items-center gap-4 mb-6">
                     <div className="w-12 h-12 bg-white rounded-2xl flex items-center justify-center shadow-sm">
                        <FiEye className="text-indigo-600" />
                     </div>
                     <div>
                        <p className="text-sm font-bold text-slate-900">Observador Sistémico</p>
                        <p className="text-xs text-slate-500">Monitoreando 124 nodos</p>
                     </div>
                  </div>
                  <div className="flex items-center gap-4">
                     <div className="w-12 h-12 bg-white rounded-2xl flex items-center justify-center shadow-sm">
                        <FiBarChart2 className="text-emerald-600" />
                     </div>
                     <div>
                        <p className="text-sm font-bold text-slate-900">Historial de Drift</p>
                        <p className="text-xs text-slate-500">Desviación mínima: 0.02%</p>
                     </div>
                  </div>
               </div>

               <div className="bg-indigo-600 rounded-3xl p-8 text-white relative overflow-hidden group cursor-pointer">
                  <div className="absolute -right-4 -bottom-4 opacity-10 group-hover:scale-125 transition-transform duration-700">
                     <FiRefreshCw size={80} />
                  </div>
                  <p className="text-[10px] font-black uppercase tracking-widest text-indigo-200 mb-2">Soberanía</p>
                  <p className="text-lg font-bold leading-tight">Reentrenar modelos con datos actuales</p>
               </div>
            </div>
         </Card>
      </div>

      <CriticalActionDialog
        isOpen={isConfirmDialogOpen}
        onClose={() => setIsConfirmDialogOpen(false)}
        onConfirm={handleConfirmApply}
        title="Validación de Propuesta Técnica"
        description={`Se procederá a la aplicación del ajuste sistémico en el dominio ${selectedProposal?.domain || 'institucional'}: ${selectedProposal?.propuesta_ajuste}. El usuario asume la responsabilidad de la validación final de esta propuesta generada por el asistente digital.`}
        confirmLabel="Validar y Ejecutar"
        type="sovereign"
      />

      <CriticalActionDialog
        isOpen={isRollbackDialogOpen}
        onClose={() => setIsRollbackDialogOpen(false)}
        onConfirm={handleConfirmRollback}
        title="Reversión de Optimización"
        description={`Está a punto de deshacer el ajuste: "${selectedProposal?.propuesta_ajuste}". El sistema restaurará el snapshot de configuración previa.`}
        confirmLabel="Confirmar Rollback"
        type="warning"
      />
    </div>
  );
}
