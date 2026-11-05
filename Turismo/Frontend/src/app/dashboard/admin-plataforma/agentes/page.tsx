'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import {
  FiCpu, FiZap, FiAlertOctagon, FiActivity, FiShield, FiPower, FiPause, FiPlay, FiTrash2
} from 'react-icons/fi';
import { sovereigntyService, AgentStatus } from '@/services/sovereigntyService';
import { ViewState } from '@/components/ui/ViewState';
import { CriticalActionDialog } from '@/components/ui/CriticalActionDialog';
import { toast } from 'react-hot-toast';

export default function AgentHierarchyControl() {
  const [agents, setAgents] = useState<AgentStatus[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState<AgentStatus | null>(null);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [actionType, setActionType] = useState<'pause' | 'kill' | 'resume'>('pause');

  useEffect(() => {
    fetchAgents();
  }, []);

  const [error, setError] = useState<string | null>(null);

  const fetchAgents = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await sovereigntyService.getAgents();
      setAgents(res.data);
    } catch (err: any) {
      console.error("Agent fetch error:", err);
      // ELIMINACIÓN DE MOCKS: El frontend refleja la ausencia de endpoint real.
      setError("BLOQUEO DE DOMINIO: El endpoint de supervisión de agentes no ha sido expuesto en el Kernel de Gobernanza.");
      setAgents([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAction = (agent: AgentStatus, type: 'pause' | 'kill' | 'resume') => {
    setSelectedAgent(agent);
    setActionType(type);
    setIsConfirmOpen(true);
  };

  const confirmAction = async () => {
    if (!selectedAgent) return;
    try {
        if (actionType === 'pause') await sovereigntyService.pauseAgent(selectedAgent.id);
        if (actionType === 'resume') await sovereigntyService.resumeAgent(selectedAgent.id);
        if (actionType === 'kill') await sovereigntyService.killAgent(selectedAgent.id);

        toast.success(`Intervención sobre ${selectedAgent.role} ejecutada.`);
        fetchAgents();
    } catch (e) {
        toast.error("Error en la ejecución soberana.");
    } finally {
        setIsConfirmOpen(false);
    }
  };

  return (
    <ViewState isLoading={isLoading} error={error}>
      <div className="space-y-10 animate-in fade-in duration-700">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-gray-100 pb-8">
            <div>
            <div className="flex items-center gap-3 mb-2">
                <div className="bg-slate-900 text-white p-2 rounded-lg">
                <FiCpu size={24} />
                </div>
                <h1 className="text-4xl font-black text-slate-900 tracking-tighter uppercase italic">Cuerpo de Funcionarios Digitales y Guardianes</h1>
            </div>
            <p className="text-slate-500 text-lg font-medium italic">Asistentes analíticos delegados que actúan como guardianes de los principios institucionales y la integridad histórica.</p>
            </div>
        </div>

        <div className="grid grid-cols-1 gap-8">
            <Card className="border-none shadow-xl bg-white rounded-[2.5rem] overflow-hidden">
                <CardHeader className="p-10 border-b border-slate-50 flex flex-row items-center justify-between bg-slate-50/30">
                    <CardTitle className="text-xl font-black uppercase tracking-widest flex items-center gap-3 italic">
                        <FiShield className="text-brand" /> Registro de Asistentes en Operación
                    </CardTitle>
                    <Badge className="bg-emerald-500 text-white font-black px-4 py-1">CERTIFICACIÓN VIGENTE</Badge>
                </CardHeader>
                <CardContent className="p-0">
                    <Table>
                        <TableHeader className="bg-slate-900 text-white">
                            <TableRow>
                                <TableHead className="font-black uppercase text-[10px] tracking-widest px-10 py-6">Funcionario / Rol</TableHead>
                                <TableHead className="font-black uppercase text-[10px] tracking-widest">Dominio</TableHead>
                                <TableHead className="font-black uppercase text-[10px] tracking-widest">Última Acción</TableHead>
                                <TableHead className="font-black uppercase text-[10px] tracking-widest">Estado</TableHead>
                                <TableHead className="font-black uppercase text-[10px] tracking-widest text-right px-10">Intervención</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {agents.map((agent) => (
                                <TableRow key={agent.id} className="hover:bg-slate-50 transition-all border-slate-100 group">
                                    <TableCell className="px-10 py-8">
                                        <div>
                                            <p className="font-black text-slate-900 text-lg uppercase italic tracking-tight">{agent.role}</p>
                                            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">{agent.hierarchy}</p>
                                        </div>
                                    </TableCell>
                                    <TableCell>
                                        <Badge variant="outline" className="font-black text-[9px] border-slate-200">{agent.domain}</Badge>
                                    </TableCell>
                                    <TableCell className="max-w-xs">
                                        <p className="text-sm font-medium text-slate-600 italic">"{agent.last_action}"</p>
                                        <p className="text-[8px] font-black text-indigo-500 uppercase mt-1 tracking-widest">Estado de Guardianía: ACTIVO</p>
                                    </TableCell>
                                    <TableCell>
                                        <div className="flex items-center gap-2">
                                            <div className={`w-2 h-2 rounded-full ${
                                                agent.status === 'ACTIVE' ? 'bg-emerald-500 animate-pulse' :
                                                agent.status === 'PAUSED' ? 'bg-amber-500' : 'bg-red-600'
                                            }`} />
                                            <span className="font-black text-xs uppercase tracking-widest">{agent.status}</span>
                                        </div>
                                    </TableCell>
                                    <TableCell className="text-right px-10">
                                        <div className="flex justify-end gap-2">
                                            {agent.status === 'ACTIVE' ? (
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    onClick={() => handleAction(agent, 'pause')}
                                                    className="border-amber-200 text-amber-600 hover:bg-amber-50 rounded-xl"
                                                >
                                                    <FiPause className="mr-2" /> Pausar
                                                </Button>
                                            ) : agent.status === 'PAUSED' ? (
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    onClick={() => handleAction(agent, 'resume')}
                                                    className="border-emerald-200 text-emerald-600 hover:bg-emerald-50 rounded-xl"
                                                >
                                                    <FiPlay className="mr-2" /> Reanudar
                                                </Button>
                                            ) : null}

                                            <Button
                                                variant="destructive"
                                                size="sm"
                                                onClick={() => handleAction(agent, 'kill')}
                                                className="bg-red-600 rounded-xl"
                                            >
                                                <FiPower className="mr-2" /> Kill-Switch
                                            </Button>
                                        </div>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>

        <CriticalActionDialog
            isOpen={isConfirmOpen}
            onClose={() => setIsConfirmOpen(false)}
            onConfirm={confirmAction}
            title="Intervención de Responsabilidad Humana"
            description={`Está a punto de modificar el estado operativo del asistente: ${selectedAgent?.role}. Esta acción queda bajo su responsabilidad directa y será registrada para fines de auditoría institucional.`}
            confirmLabel="Confirmar Intervención"
            type={actionType === 'kill' ? 'danger' : 'sovereign'}
        />
      </div>
    </ViewState>
  );
}
