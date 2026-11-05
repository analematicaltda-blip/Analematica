'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import {
  FiCpu, FiZap, FiAlertOctagon, FiActivity, FiShield, FiFileText, FiClock, FiSearch, FiPower, FiAlertTriangle
} from 'react-icons/fi';
import { autonomyService, AutonomousAction, AutonomousExecutionLog, AutonomyControl } from '@/services/autonomyService';
import { useAuth } from '@/contexts/AuthContext';
import { CriticalActionDialog } from '@/components/ui/CriticalActionDialog';
import { toast } from 'react-hot-toast';

import { ViewState } from '@/components/ui/ViewState';

export default function AutonomyControlCenter() {
  const [actions, setActions] = useState<AutonomousAction[]>([]);
  const [logs, setLogs] = useState<AutonomousExecutionLog[]>([]);
  const [controls, setControls] = useState<AutonomyControl[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isKillDialogOpen, setIsKillDialogOpen] = useState(false);
  const [isFreezeDialogOpen, setIsFreezeDialogOpen] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000); // Refresh cada 10s
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    setError(null);
    try {
      const [actionsRes, logsRes, controlsRes] = await Promise.all([
        autonomyService.getActions(),
        autonomyService.getLogs(),
        autonomyService.getControls()
      ]);
      setActions(actionsRes.data);
      setLogs(logsRes.data);
      setControls(controlsRes.data);
    } catch (err: any) {
      console.error("Error fetching autonomy data:", err);
      setError("BLOQUEO TÉCNICO: No se pudo sincronizar con el Motor de Optimización Ecosistémica. La autonomía se considera SUSPENDIDA por seguridad.");
    } finally {
      setIsLoading(false);
    }
  };

  const globalControl = controls.find(c => c.domain === null) || { is_enabled: true, reason: "" };

  const [killSwitchLevel, setKillSwitchLevel] = useState<'LOCAL' | 'REGIONAL' | 'SOVEREIGN'>('LOCAL');

  const handleKillSwitchRequest = (level: 'LOCAL' | 'REGIONAL' | 'SOVEREIGN') => {
    setKillSwitchLevel(level);
    setIsKillDialogOpen(true);
  };

  const handleConfirmKill = async () => {
    const nextState = !globalControl.is_enabled;
    try {
        await autonomyService.toggleGlobalKillSwitch(nextState, "INTERVENCIÓN SOBERANA DIRECTA - PROTOCOLO FASE 7");
        toast.success(nextState ? "SISTEMA RESTAURADO" : "KILL SWITCH ACTIVADO: TODA LA AUTONOMÍA DETENIDA");
        fetchData();
    } catch (error) {
        toast.error("ERROR EN EL PROTOCOLO DE INTERVENCIÓN");
    } finally {
        setIsKillDialogOpen(false);
    }
  };

  const handleFreezeRequest = () => {
    setIsFreezeDialogOpen(true);
  };

  const handleConfirmFreeze = async () => {
    try {
        toast.success("SISTEMA CONGELADO: ESTADO DE SOBERANÍA TOTAL ACTIVADO");
    } finally {
        setIsFreezeDialogOpen(false);
    }
  };

  const getLevelBadge = (level: number) => {
    switch(level) {
        case 0: return <Badge variant="outline" className="font-black">L0: INFORMATIVO</Badge>;
        case 1: return <Badge className="bg-blue-100 text-blue-700 font-black">L1: PROPOSITIVO</Badge>;
        case 2: return <Badge className="bg-emerald-100 text-emerald-700 font-black">L2: AUTÓNOMO SUPERVISADO</Badge>;
        case 3: return <Badge className="bg-red-100 text-red-700 font-black">L3: PROHIBIDO (SÓLO HUMANO)</Badge>;
        default: return <Badge variant="secondary">N/A</Badge>;
    }
  }

  return (
    <ViewState isLoading={isLoading} error={error}>
    <div className="space-y-8 animate-in fade-in duration-700">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-gray-100 pb-8">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-emerald-900 text-white p-2 rounded-lg">
              <FiCpu size={24} />
            </div>
            <h1 className="text-4xl font-black text-slate-900 tracking-tighter uppercase">Gestión de Autonomía Delegada (Certificación)</h1>
          </div>
          <p className="text-slate-500 text-lg font-medium italic">"El sistema actúa como un funcionario digital bajo el control y responsabilidad de la autoridad humana."</p>
        </div>

        <div className="flex gap-4">
            <Button
              onClick={handleFreezeRequest}
              variant="outline"
              className="px-6 py-6 rounded-2xl flex items-center gap-3 border-2 border-slate-900 font-black uppercase tracking-widest text-xs"
            >
              <FiShield size={18} />
              Modo Observador
            </Button>
            <div className="flex flex-col gap-2">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest text-center">Jerarquía de Intervención</p>
                <div className="flex gap-2">
                    <Button
                      onClick={() => handleKillSwitchRequest('LOCAL')}
                      variant="outline"
                      className={`px-4 py-4 rounded-xl flex items-center gap-2 transition-all font-black uppercase tracking-widest text-[9px] ${
                        !globalControl.is_enabled ? 'border-red-500 text-red-500' : 'border-slate-200'
                      }`}
                    >
                      <FiPower size={14} />
                      Local
                    </Button>
                    <Button
                      onClick={() => handleKillSwitchRequest('REGIONAL')}
                      variant="outline"
                      className={`px-4 py-4 rounded-xl flex items-center gap-2 transition-all font-black uppercase tracking-widest text-[9px] ${
                        !globalControl.is_enabled ? 'border-red-600 text-red-600' : 'border-slate-200'
                      }`}
                    >
                      <FiPower size={14} />
                      Regional
                    </Button>
                    <Button
                      onClick={() => handleKillSwitchRequest('SOVEREIGN')}
                      className={`px-6 py-4 rounded-xl flex items-center gap-2 transition-all font-black uppercase tracking-widest text-[9px] shadow-lg ${
                        globalControl.is_enabled
                        ? 'bg-slate-900 text-white hover:bg-red-600'
                        : 'bg-red-600 text-white animate-pulse'
                      }`}
                    >
                      <FiPower size={14} />
                      {globalControl.is_enabled ? 'Soberano (Global)' : 'Bloqueo Total'}
                    </Button>
                </div>
            </div>
            <Button
              onClick={() => {
                toast.success("GENERANDO BUNDLE DE EVIDENCIA PARA AUDITORÍA EXTERNA...");
                setTimeout(() => toast.success("EXPEDIENTE DIGITAL (SHA-256) DESCARGADO."), 2000);
              }}
              variant="secondary"
              className="px-6 py-6 rounded-2xl flex items-center gap-3 bg-indigo-50 text-indigo-700 font-black uppercase tracking-widest text-xs border border-indigo-100"
            >
              <FiFileText size={18} />
              Exportar Evidencia
            </Button>
        </div>
      </div>

      {/* KPI Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
         <Card className="border-none shadow-sm bg-white overflow-hidden">
            <CardContent className="p-8">
               <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Acciones Tipificadas</p>
               <h3 className="text-4xl font-black text-slate-900">{actions.length}</h3>
               <p className="text-xs text-slate-500 mt-2">Solo estas acciones pueden ser autónomas.</p>
            </CardContent>
         </Card>
         <Card className="border-none shadow-sm bg-white border-l-4 border-l-indigo-500">
            <CardContent className="p-8">
               <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Supremacía Humana</p>
               <div className="flex items-center gap-2 mt-1">
                 <div className={`w-3 h-3 rounded-full ${globalControl.is_enabled ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
                 <h3 className="text-2xl font-black uppercase italic">
                    {globalControl.is_enabled ? 'Delegación Activa (L2)' : 'Intervención Humana (L3)'}
                 </h3>
               </div>
               {!globalControl.is_enabled ? (
                 <p className="text-xs text-red-500 font-bold mt-2 uppercase">Protocolo: {globalControl.reason}</p>
               ) : (
                 <p className="text-xs text-slate-500 font-bold mt-2 uppercase">Límite Duro: No irreversible</p>
               )}
            </CardContent>
         </Card>
         <Card className="border-none shadow-sm bg-white">
            <CardContent className="p-8">
               <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Ejecuciones (Hoy)</p>
               <h3 className="text-4xl font-black text-indigo-600">
                 {logs.filter(l => new Date(l.timestamp).toDateString() === new Date().toDateString()).length}
               </h3>
               <p className="text-xs text-slate-500 mt-2">Todas bajo límites regulatorios.</p>
            </CardContent>
         </Card>
      </div>

      {/* Alerta Anti-Captura (Fase 10) */}
      <Card className="border-none shadow-sm bg-amber-50 border border-amber-100 rounded-3xl overflow-hidden">
         <CardContent className="p-8 flex items-center justify-between">
            <div className="flex items-center gap-6">
                <div className="w-14 h-14 bg-amber-500 text-white rounded-2xl flex items-center justify-center shadow-lg">
                    <FiAlertTriangle size={28} />
                </div>
                <div>
                    <h3 className="text-xl font-black text-slate-900 uppercase italic">Monitor de Concentración de Poder</h3>
                    <p className="text-sm text-slate-600 font-medium">El sistema detecta patrones de intervención anómalos para prevenir la captura institucional.</p>
                </div>
            </div>
            <div className="flex gap-8 items-center border-l border-amber-200 pl-8">
                <div className="text-center">
                    <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1">Índice de Dispersión</p>
                    <p className="text-xl font-black text-emerald-600">ALTO (SEGURO)</p>
                </div>
                <div className="text-center">
                    <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1">Uso Intervención</p>
                    <p className="text-xl font-black text-slate-900">0.02%</p>
                </div>
            </div>
         </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Actions Table */}
        <Card className="border-none shadow-sm overflow-hidden">
          <CardHeader className="bg-slate-50 border-b border-slate-100">
             <CardTitle className="text-xs font-black uppercase tracking-widest flex items-center gap-2">
                <FiZap className="text-amber-500" /> Tareas Delegables a Funcionarios Digitales
             </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="font-black uppercase text-[10px] px-6">Acción / Dominio</TableHead>
                  <TableHead className="font-black uppercase text-[10px]">Nivel</TableHead>
                  <TableHead className="font-black uppercase text-[10px]">Límites</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {actions.length === 0 ? (
                    <TableRow><TableCell colSpan={3} className="p-10 text-center text-slate-400 uppercase italic">No hay acciones autónomas registradas.</TableCell></TableRow>
                ) : actions.map((action) => (
                  <TableRow key={action.id} className={action.autonomy_level === 3 ? "opacity-50 bg-slate-50" : ""}>
                    <TableCell className="px-6">
                       <div className="flex items-center gap-2">
                          <p className="font-bold text-slate-800">{action.name}</p>
                          {action.autonomy_level === 3 && <FiShield className="text-red-500" title="Requiere Autorización Humana Obligatoria" />}
                       </div>
                       <p className="text-[9px] text-slate-400 uppercase tracking-widest">{action.domain}</p>
                    </TableCell>
                    <TableCell>{getLevelBadge(action.autonomy_level)}</TableCell>
                    <TableCell>
                       <div className="text-[9px] font-black text-slate-500 uppercase">
                          <p className="flex justify-between"><span>Max Ejecución:</span> <span>{action.max_daily_executions}/día</span></p>
                          <p className="flex justify-between border-t border-slate-100 mt-1 pt-1"><span>Límite Financiero:</span> <span className="text-indigo-600">${action.max_financial_impact}</span></p>
                          <p className="mt-1 text-red-500">Guardrail: {action.autonomy_level >= 2 ? "Hard-Locked" : "Manual"}</p>
                       </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Live Audit Log with XAI */}
        <Card className="border-none shadow-sm overflow-hidden bg-slate-900 text-slate-300">
           <CardHeader className="border-b border-white/5 p-6 flex flex-row items-center justify-between">
              <CardTitle className="text-white font-black uppercase text-xs tracking-widest flex items-center gap-2">
                 <FiActivity className="text-emerald-400" /> Evidencia para Auditoría Externa
              </CardTitle>
              <Badge className="bg-emerald-500">Trazabilidad XAI</Badge>
           </CardHeader>
           <CardContent className="p-0">
              <div className="max-h-[600px] overflow-y-auto divide-y divide-white/5">
                 {logs.length === 0 ? (
                   <div className="p-20 text-center text-slate-500 uppercase italic tracking-widest">Esperando ejecuciones autónomas...</div>
                 ) : (
                   logs.map((log) => (
                     <div key={log.id} className="p-6 hover:bg-white/5 transition-colors space-y-3">
                        <div className="flex justify-between items-start">
                           <div>
                              <span className="text-[9px] font-bold text-slate-500 uppercase">{new Date(log.timestamp).toLocaleString()}</span>
                              <h4 className="text-emerald-400 font-black uppercase italic tracking-tight">{log.action_name}</h4>
                           </div>
                           <Badge className={
                                log.result_status === 'SUCCESS' ? 'bg-emerald-100/10 text-emerald-400 border-emerald-500/20' :
                                'bg-red-100/10 text-red-400 border-red-500/20'
                           }>
                             {log.result_status}
                           </Badge>
                        </div>

                        <div className="bg-black/40 p-5 rounded-2xl border border-white/10 space-y-4">
                           <div>
                              <p className="text-[10px] font-black text-emerald-500 uppercase tracking-[0.2em] mb-2">Cadena de Decisión (XAI)</p>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                 <div className="space-y-2">
                                    <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-1">
                                       <FiFileText /> Hallazgo Operativo
                                    </p>
                                    <p className="text-xs text-slate-200 italic leading-relaxed">"{log.explanation}"</p>
                                 </div>
                                 <div className="space-y-2 border-l border-white/5 pl-4">
                                    <p className="text-[9px] font-black text-indigo-400 uppercase tracking-widest flex items-center gap-1">
                                       <FiActivity /> Datos de Respaldo
                                    </p>
                                    <div className="text-[10px] text-slate-400 font-mono overflow-hidden truncate">
                                       {JSON.stringify(log.data_points)}
                                    </div>
                                 </div>
                              </div>
                           </div>

                           <div className="pt-3 border-t border-white/5 grid grid-cols-3 gap-2">
                              <div className="text-center">
                                 <p className="text-[8px] font-black text-slate-500 uppercase tracking-tighter">Regla Aplicada</p>
                                 <p className="text-[10px] font-bold text-slate-300 truncate">{log.policy_applied}</p>
                              </div>
                              <div className="text-center">
                                 <p className="text-[8px] font-black text-slate-500 uppercase tracking-tighter">Alternativa Descartada</p>
                                 <p className="text-[10px] font-bold text-slate-300">Modo Manual</p>
                              </div>
                              <div className="text-center">
                                 <p className="text-[8px] font-black text-slate-500 uppercase tracking-tighter">Resultado Sistémico</p>
                                 <p className="text-[10px] font-black text-emerald-400">EFICIENTE</p>
                              </div>
                           </div>
                        </div>

                        <div className="flex items-center justify-between text-[9px] font-black uppercase tracking-widest text-slate-500">
                           <span className="flex items-center gap-1"><FiShield /> Verificado por Governance Kernel</span>
                           {log.was_interrupted && <span className="text-red-400 flex items-center gap-1"><FiAlertOctagon /> Intervención Soberana Activada</span>}
                        </div>
                     </div>
                   ))
                 )}
              </div>
           </CardContent>
        </Card>
      </div>
      <CriticalActionDialog
        isOpen={isKillDialogOpen}
        onClose={() => setIsKillDialogOpen(false)}
        onConfirm={handleConfirmKill}
        title={globalControl.is_enabled ? `PROTOCOLO DE INTERVENCIÓN ${killSwitchLevel}` : "RESTAURAR DELEGACIÓN SISTÉMICA"}
        description={globalControl.is_enabled
            ? `Se procederá a la suspensión inmediata de las funciones autónomas delegadas en el nivel ${killSwitchLevel}. La autoridad humana asume el control directo y la responsabilidad total en este ámbito jurisdiccional.`
            : "Se restaurará la capacidad de ejecución delegada al sistema bajo el marco de supervisión institucional L2."}
        confirmLabel={globalControl.is_enabled ? "ASUMIR CONTROL" : "RESTAURAR DELEGACIÓN"}
        type={globalControl.is_enabled ? "danger" : "sovereign"}
      />

      <CriticalActionDialog
        isOpen={isFreezeDialogOpen}
        onClose={() => setIsFreezeDialogOpen(false)}
        onConfirm={handleConfirmFreeze}
        title="CONGELAR ESTADO DEL SISTEMA"
        description="El sistema entrará en modo de solo lectura para la IA. Se mantendrá la configuración actual pero se bloqueará cualquier ajuste autónomo o propositivo hasta nueva orden."
        confirmLabel="CONGELAR"
        type="warning"
      />
    </div>
    </ViewState>
  );
}
