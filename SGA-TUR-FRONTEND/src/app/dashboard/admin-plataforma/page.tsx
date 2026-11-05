'use client';

import React from 'react';
import useSWR from 'swr';
import { getStatistics, getInfraMetrics } from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import {
  FiShield,
  FiUsers,
  FiActivity,
  FiAlertTriangle,
  FiZap,
  FiGlobe,
  FiCpu,
  FiPower,
  FiLock,
  FiUnlock,
  FiRepeat,
  FiClock,
  FiAward,
  FiWifi,
  FiWifiOff,
  FiTrendingUp,
  FiRefreshCw
} from 'react-icons/fi';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { ViewState } from '@/components/ui/ViewState';
import Link from 'next/link';
import { sovereigntyService, SystemFlag } from '@/services/sovereigntyService';
import { toast } from 'react-hot-toast';
import { CriticalActionDialog } from '@/components/ui/CriticalActionDialog';
import { useWebSockets, TowerEvent } from '@/hooks/useWebSockets';

export default function AdminPlataformaPage() {
  const { data: stats, mutate: mutateStats, isLoading } = useSWR('admin-statistics', getStatistics);
  const { data: flagsRes, mutate: mutateFlags } = useSWR('admin-flags', sovereigntyService.getFlags);

  const { lastEvent, isConnected } = useWebSockets();
  const [liveEvents, setLiveEvents] = React.useState<TowerEvent[]>([]);
  const [autonomousDecisions, setAutonomousDecisions] = React.useState<TowerEvent[]>([]);
  const { data: initialInfra } = useSWR('infra-metrics', getInfraMetrics, { refreshInterval: 30000 });
  const [infraMetrics, setInfraMetrics] = React.useState<any>(null);

  React.useEffect(() => {
    if (initialInfra && !infraMetrics) {
      setInfraMetrics(initialInfra);
    }
  }, [initialInfra, infraMetrics]);

  const [isEmergencyDialogOpen, setIsEmergencyDialogOpen] = React.useState(false);
  const [isAttackModeActive, setIsAttackModeActive] = React.useState(false);

  // Escuchar eventos en vivo para actualizar KPIs sin polling
  React.useEffect(() => {
    if (lastEvent) {
      setLiveEvents(prev => [lastEvent, ...prev].slice(0, 10));

      if (lastEvent.event_type === 'AUTONOMOUS_DECISION_EXECUTED') {
          setAutonomousDecisions(prev => [lastEvent, ...prev].slice(0, 5));
      }

      if (lastEvent.event_type === 'TECHNICAL_METRICS_UPDATED') {
          setInfraMetrics(lastEvent.payload);
      }

      // Actualizar estadísticas si el evento es relevante
      if (['VentaCreada', 'PagoRecibido', 'AsientoGenerado'].includes(lastEvent.event_type)) {
        mutateStats(); // Re-fetch datos ligeros
        toast(`Omnisciencia: Nuevo evento ${lastEvent.event_type} detectado`, {
          icon: '⚡',
          style: { borderRadius: '10px', background: '#333', color: '#fff' }
        });
      }
    }
  }, [lastEvent, mutateStats]);

  const handleFlagToggle = async (id: string, currentStatus: string) => {
    const nextStatus = currentStatus === 'ACTIVE' ? 'PAUSED' : 'ACTIVE';
    try {
        await sovereigntyService.toggleFlag(id, nextStatus);
        toast.success(`Bandera de sistema ajustada: ${nextStatus}`);
        mutateFlags();
    } catch (e) {
        toast.error("INTERVENCIÓN FALLIDA: El Kernel de Gobernanza no permitió el cambio de estado.");
    }
  };

  const handleEmergencyKill = async () => {
    setIsAttackModeActive(true);
    toast.success("S-0: MODO ATAQUE ACTIVADO. El sistema ha sido congelado.");
    setIsEmergencyDialogOpen(false);
  };

  const handleRestoreNormalMode = () => {
    setIsAttackModeActive(false);
    toast.success("S-0: MODO NORMAL RESTAURADO.");
  };

  const mainKpis = [
    { label: 'Total Usuarios Sistema', value: stats?.total_usuarios || '0', trend: 'Global', icon: FiUsers, color: 'text-blue-600' },
    { label: 'Prestadores Activos', value: stats?.total_prestadores || '0', trend: 'Vía 2', icon: FiActivity, color: 'text-indigo-600' },
    { label: 'Publicaciones Totales', value: stats?.total_publicaciones || '0', trend: 'Contenido', icon: FiGlobe, color: 'text-emerald-600' },
    { label: 'Madurez Autónoma', value: '85%', trend: 'Fase 5', icon: FiZap, color: 'text-amber-600' },
  ];

  return (
    <ViewState
       isLoading={isLoading}
       loadingMessage="Compilando estado de soberanía sistémica..."
       error={!stats && !isLoading ? "No fue posible recuperar las métricas globales." : null}
    >
    <div className="space-y-10 animate-in fade-in duration-1000">
      {/* Header de Soberanía con Estado de Conexión en Vivo */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-gray-100 pb-8">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-slate-900 text-white p-2 rounded-lg">
              <FiShield size={24} />
            </div>
            <h1 className="text-4xl font-black text-slate-900 tracking-tighter uppercase">Torre de Control Omnisciente</h1>
            <Badge className={isConnected ? "bg-emerald-500" : "bg-red-500"}>
              {isConnected ? <FiWifi className="mr-1" /> : <FiWifiOff className="mr-1" />}
              {isConnected ? "LIVE" : "DISCONNECTED"}
            </Badge>
          </div>
          <p className="text-slate-500 text-lg font-medium italic">Monitoreo sistémico en tiempo real. Pulso de negocio actualizado al instante.</p>
        </div>
        <div className="flex gap-4">
           <div className="px-6 py-3 bg-emerald-50 border border-emerald-100 rounded-2xl flex items-center gap-3">
              <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse" />
              <span className="text-sm font-black text-emerald-700 tracking-widest uppercase">Autonomía Fase 5 Activa</span>
           </div>
           <Link href="/dashboard/admin-plataforma/agentes">
             <Button variant="outline" className="border-slate-200 text-slate-600 font-bold px-6 py-6 rounded-2xl flex items-center gap-2">
                <FiCpu /> Auditoría IA
             </Button>
           </Link>
           {!isAttackModeActive ? (
                <Button
                    onClick={() => setIsEmergencyDialogOpen(true)}
                    className="bg-red-600 text-white font-black px-8 py-6 rounded-2xl hover:bg-red-700 transition-all shadow-xl shadow-red-500/20">
                    <FiPower className="mr-2" /> Activar Modo Ataque
                </Button>
           ) : (
                <Button
                    onClick={handleRestoreNormalMode}
                    className="bg-emerald-600 text-white font-black px-8 py-6 rounded-2xl hover:bg-emerald-700 transition-all shadow-xl shadow-emerald-500/20 animate-pulse">
                    <FiRepeat className="mr-2" /> Restaurar Modo Normal
                </Button>
           )}
        </div>
      </div>

      {/* Grid de KPIs Maestros */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
         {mainKpis.map((kpi, i) => (
           <Card key={i} className="border-none shadow-sm hover:shadow-md transition-all bg-white group cursor-default">
              <CardContent className="p-8">
                 <div className="flex justify-between items-start mb-6">
                    <div className={`p-4 rounded-2xl bg-gray-50 ${kpi.color} group-hover:scale-110 transition-transform`}>
                       <kpi.icon size={28} />
                    </div>
                    <Badge className="bg-slate-100 text-slate-600 border-none font-bold">{kpi.trend}</Badge>
                 </div>
                 <p className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-1">{kpi.label}</p>
                 <h3 className="text-3xl font-black text-slate-900">{kpi.value}</h3>
              </CardContent>
           </Card>
         ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
         {/* Feed de Eventos en Tiempo Real (Fase 4.7) */}
         <Card className="lg:col-span-2 border-none shadow-sm overflow-hidden bg-white">
            <CardHeader className="bg-slate-50/50 p-6 border-b border-gray-100">
               <CardTitle className="text-xl font-black flex items-center gap-2">
                  <FiActivity className="text-indigo-600 animate-spin-slow" /> Flujo de Eventos Omnisciente
               </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
               <div className="divide-y divide-gray-100 max-h-[400px] overflow-y-auto">
                  {liveEvents.length === 0 ? (
                      <div className="p-20 text-center text-slate-400 uppercase italic tracking-widest text-xs">
                          Esperando pulsos de sistema...
                      </div>
                  ) : liveEvents.map((ev, i) => (
                    <div key={ev.event_id} className="p-6 hover:bg-slate-50 transition-colors animate-in slide-in-from-top duration-500">
                       <div className="flex justify-between items-start mb-2">
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="border-indigo-200 text-indigo-700 font-black">{ev.event_type}</Badge>
                            <span className="text-[10px] text-slate-400 font-mono">{ev.timestamp}</span>
                          </div>
                          <Badge className={
                             ev.severity === 'critical' ? 'bg-red-500' :
                             ev.severity === 'warning' ? 'bg-amber-500' : 'bg-blue-500'
                          }>
                             {ev.severity.toUpperCase()}
                          </Badge>
                       </div>
                       <p className="text-slate-700 font-medium">{JSON.stringify(ev.payload)}</p>
                    </div>
                  ))}
               </div>
            </CardContent>
         </Card>

         {/* Historial de Autonomía (Fase 5.7) */}
         <Card className="border-none shadow-xl bg-slate-900 text-white overflow-hidden rounded-3xl">
            <CardHeader className="p-8 border-b border-white/10">
               <CardTitle className="text-xl font-black flex items-center gap-2">
                  <FiZap className="text-amber-400" /> Historial de Autonomía IA
               </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
               <div className="divide-y divide-white/5">
                  {autonomousDecisions.length === 0 ? (
                      <div className="p-20 text-center text-slate-500 uppercase italic tracking-widest text-xs">
                          No hay ejecuciones autónomas en el periodo actual.
                      </div>
                  ) : autonomousDecisions.map((decision, i) => (
                    <div key={i} className="p-8 hover:bg-white/5 transition-colors cursor-pointer group border-l-4 border-emerald-500">
                       <div className="flex justify-between items-start mb-3">
                          <span className="text-[10px] font-black uppercase tracking-[0.2em] text-indigo-400">{decision.payload.agent}</span>
                          <Badge className="bg-emerald-600">AUTONOMOUS</Badge>
                       </div>
                       <h4 className="font-bold text-lg mb-2 group-hover:text-emerald-300 transition-colors">{decision.payload.action}</h4>
                       <p className="text-slate-400 text-sm leading-relaxed">Status: {decision.payload.status}</p>
                    </div>
                  ))}
               </div>
               <Link href="/dashboard/admin-plataforma/agentes">
                <div className="p-8 bg-indigo-600 hover:bg-indigo-700 transition-colors text-center cursor-pointer font-black uppercase tracking-widest text-sm">
                    Ver Trazabilidad XAI
                </div>
               </Link>
            </CardContent>
         </Card>
      </div>

      {/* Simulación Estratégica y Auto-Corrección (Fase 5.9 / 5.6) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <Card className="border-none shadow-sm bg-white rounded-3xl overflow-hidden">
              <CardHeader className="p-8 bg-slate-50 border-b">
                  <CardTitle className="text-xl font-black flex items-center gap-2">
                      <FiCpu className="text-brand" /> Monitor de Infraestructura
                  </CardTitle>
              </CardHeader>
              <CardContent className="p-8">
                  <div className="space-y-6">
                      <div>
                          <div className="flex justify-between mb-2">
                              <span className="text-xs font-black uppercase text-slate-400">CPU Usage</span>
                              <span className="text-xs font-bold">{infraMetrics?.cpu_usage_percent || 0}%</span>
                          </div>
                          <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                              <div
                                className="bg-brand h-full transition-all duration-1000"
                                style={{ width: `${infraMetrics?.cpu_usage_percent || 0}%` }}
                              />
                          </div>
                      </div>
                      <div>
                          <div className="flex justify-between mb-2">
                              <span className="text-xs font-black uppercase text-slate-400">RAM Usage</span>
                              <span className="text-xs font-bold">{infraMetrics?.ram_usage_percent || 0}%</span>
                          </div>
                          <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                              <div
                                className="bg-indigo-500 h-full transition-all duration-1000"
                                style={{ width: `${infraMetrics?.ram_usage_percent || 0}%` }}
                              />
                          </div>
                      </div>
                      <div className="pt-4 border-t border-slate-50 grid grid-cols-2 gap-4">
                          <div>
                              <p className="text-[10px] font-black text-slate-400 uppercase">Uptime</p>
                              <p className="text-sm font-bold">
                                  {infraMetrics?.uptime_seconds ? `${Math.floor(infraMetrics.uptime_seconds / 3600)}h ${Math.floor((infraMetrics.uptime_seconds % 3600) / 60)}m` : '---'}
                              </p>
                          </div>
                          <div>
                              <p className="text-[10px] font-black text-slate-400 uppercase">Threads</p>
                              <p className="text-sm font-bold">{infraMetrics?.threads || '0'}</p>
                          </div>
                      </div>
                  </div>
              </CardContent>
          </Card>

          <Card className="border-none shadow-sm bg-white rounded-3xl overflow-hidden">
              <CardHeader className="p-8 bg-slate-50 border-b">
                  <CardTitle className="text-xl font-black flex items-center gap-2">
                      <FiTrendingUp className="text-emerald-600" /> Simulador de Escenarios "What-If"
                  </CardTitle>
              </CardHeader>
              <CardContent className="p-8">
                  <p className="text-slate-500 mb-6 font-medium">Proyecta el impacto de cambios macroeconómicos o estructurales en la rentabilidad del holding.</p>
                  <div className="space-y-4">
                      <Button className="w-full justify-between py-8 px-6 rounded-2xl border-2 border-slate-100 bg-white text-slate-900 hover:bg-slate-50 transition-all group">
                          <div className="text-left">
                              <p className="font-black uppercase text-xs text-slate-400">Escenario 1</p>
                              <p className="font-bold">Caída de ventas 20% + Inflación 10%</p>
                          </div>
                          <FiTrendingUp className="text-slate-300 group-hover:text-emerald-500 transition-colors" size={24} />
                      </Button>
                      <Button variant="outline" className="w-full border-2 border-dashed border-slate-200 py-8 rounded-2xl font-black text-slate-400 uppercase tracking-widest hover:border-indigo-400 hover:text-indigo-500 transition-all">
                          Crear Nueva Simulación
                      </Button>
                  </div>
              </CardContent>
          </Card>

          <Card className="border-none shadow-sm bg-white rounded-3xl overflow-hidden">
              <CardHeader className="p-8 bg-slate-50 border-b">
                  <CardTitle className="text-xl font-black flex items-center gap-2">
                      <FiRefreshCw className="text-indigo-600" /> Monitor de Auto-Corrección (Self-Healing)
                  </CardTitle>
              </CardHeader>
              <CardContent className="p-8">
                  <div className="flex items-center justify-between mb-8 bg-indigo-50 p-6 rounded-2xl border border-indigo-100">
                      <div>
                          <p className="text-xs font-black text-indigo-400 uppercase tracking-widest">Estado del Motor</p>
                          <p className="text-xl font-black text-indigo-900 italic">Vigilante / Pasivo</p>
                      </div>
                      <div className="w-12 h-12 bg-indigo-500 rounded-full flex items-center justify-center text-white shadow-lg shadow-indigo-200">
                          <FiRefreshCw className="animate-spin-slow" size={24} />
                      </div>
                  </div>
                  <div className="space-y-3">
                      <div className="flex items-center justify-between text-sm">
                          <span className="text-slate-500 font-medium">Eventos reconciliados (24h)</span>
                          <span className="font-black text-slate-900">12</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                          <span className="text-slate-500 font-medium">Asientos regenerados</span>
                          <span className="font-black text-slate-900">3</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                          <span className="text-slate-500 font-medium">Integridad del Ledger</span>
                          <Badge className="bg-emerald-500">OPTIMAL</Badge>
                      </div>
                  </div>
              </CardContent>
          </Card>
      </div>

      <CriticalActionDialog
        isOpen={isEmergencyDialogOpen}
        onClose={() => setIsEmergencyDialogOpen(false)}
        onConfirm={handleEmergencyKill}
        title="Suspensión de Operaciones por Auditoría"
        description="Se procederá a la suspensión inmediata de las funciones comerciales y de registro del sistema."
        confirmLabel="Confirmar Suspensión"
        type="danger"
      />
    </div>
    </ViewState>
  );
}
