'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import {
  FiPlay,
  FiCheckCircle,
  FiAlertCircle,
  FiClock,
  FiUser,
  FiLayers,
  FiMoreVertical,
  FiArrowRight,
  FiPlus,
  FiSearch,
  FiFilter,
  FiActivity,
  FiClipboard,
  FiBarChart2,
  FiUpload,
  FiMessageSquare,
  FiPauseCircle,
  FiTrendingUp,
  FiUsers
} from 'react-icons/fi';

// --- TIPOS OPERATIVOS ---
type OperationalStatus = 'PENDIENTE' | 'PREPARACION' | 'EJECUCION' | 'VALIDACION' | 'COMPLETADA' | 'INCIDENCIA' | 'CANCELADA';

interface Tarea {
    id: string;
    nombre: string;
    responsable: string;
    rol: 'OPERADOR' | 'SUPERVISOR' | 'SOPORTE';
    estado: 'PENDIENTE' | 'EN_PROGRESO' | 'LISTO' | 'BLOQUEADO';
    fecha_limite: string;
    dependencias: string[]; // IDs de tareas que deben terminar antes
    comentarios: string[];
    evidencias: string[];
}

interface Operacion {
    id: string;
    venta_id: string;
    servicio_nombre: string;
    cliente_nombre: string;
    estado: OperationalStatus;
    progreso: number;
    fecha_inicio: string;
    fecha_fin_estimada: string;
    responsable_lider: string;
    actividades: {
        id: string;
        nombre: string;
        tareas: Tarea[];
    }[];
    incidencias: {
        id: string;
        titulo: string;
        estado: 'ABIERTA' | 'RESOLUCION' | 'RESUELTA' | 'ESCALADA';
        prioridad: 'ALTA' | 'MEDIA' | 'BAJA';
        fecha: string;
    }[];
}

import { ViewState } from '@/components/ui/ViewState';
import api from '@/services/api';
import { toast } from 'react-toastify';

import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';

export default function CentroOperativoPage() {
    const { getOrdenesOperativas, updateOrdenEstado, reportIncidente, isLoading: apiLoading } = useMiNegocioApi();
    const [operations, setOperations] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);
 
    const [selectedOpId, setSelectedOpId] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState<'PANEL' | 'TAREAS' | 'INCIDENCIAS' | 'METRICAS'>('PANEL');
    const [isNewOpModalOpen, setIsNewOpModalOpen] = useState(false);

    const loadOperations = useCallback(async () => {
        setIsLoading(true);
        const data = await getOrdenesOperativas();
        if (data) {
            setOperations(data.results || data);
        }
        setIsLoading(false);
    }, [getOrdenesOperativas]);

    useEffect(() => {
        loadOperations();
    }, [loadOperations]);
 

    const selectedOp = operations.find(o => o.id === selectedOpId);

    const updateTaskStatus = (opId: string, taskId: string, newStatus: Tarea['estado']) => {
        setOperations(prev => prev.map(op => {
            if (op.id !== opId) return op;
            return {
                ...op,
                actividades: op.actividades.map(act => ({
                    ...act,
                    tareas: act.tareas.map(t => {
                        if (t.id !== taskId) return t;
                        return { ...t, estado: newStatus };
                    })
                }))
            };
        }));
    };

    const resolveIncident = (opId: string, incId: string) => {
        setOperations(prev => prev.map(op => {
            if (op.id !== opId) return op;
            const updatedIncidencias = op.incidencias.map(inc => {
                if (inc.id !== incId) return inc;
                return { ...inc, estado: 'RESUELTA' as const };
            });
            // Si no quedan incidencias abiertas, volver a EJECUCION
            const hasOpenIncidents = updatedIncidencias.some(inc => inc.estado !== 'RESUELTA');
            return {
                ...op,
                estado: hasOpenIncidents ? 'INCIDENCIA' : 'EJECUCION',
                incidencias: updatedIncidencias
            };
        }));
    };

    const addIncident = (opId: string, title: string) => {
        setOperations(prev => prev.map(op => {
            if (op.id !== opId) return op;
            const newInc = {
                id: `INC-${Date.now()}`,
                titulo: title,
                estado: 'ABIERTA' as const,
                prioridad: 'ALTA' as const,
                fecha: new Date().toISOString().split('T')[0]
            };
            return {
                ...op,
                estado: 'INCIDENCIA' as const,
                incidencias: [newInc, ...op.incidencias]
            };
        }));
    };

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-black transition-colors flex flex-col">
            {/* Header Corporativo del Centro de Operaciones */}
            <div className="bg-white dark:bg-brand-deep/10 border-b border-slate-100 dark:border-white/5 p-8">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div>
                        <h1 className="text-4xl font-black text-slate-900 dark:text-white tracking-tighter uppercase italic flex items-center gap-3">
                            <FiActivity className="text-brand" /> Centro de Operaciones
                        </h1>
                        <p className="text-slate-500 dark:text-slate-400 mt-2 text-lg font-medium">Control de ejecución empresarial en tiempo real.</p>
                    </div>
                    <div className="flex gap-3">
                        <Button
                            className="bg-brand text-white font-black px-6 rounded-xl shadow-lg shadow-brand/20"
                            onClick={() => setIsNewOpModalOpen(true)}
                        >
                            <FiPlus className="mr-2" /> Nueva Operación
                        </Button>
                        <Button variant="outline" className="border-slate-200 dark:border-white/10 font-bold px-6 rounded-xl">
                            <FiFilter className="mr-2" /> Filtros
                        </Button>
                    </div>
                </div>

                {/* Sub-tabs Operativos */}
                <div className="flex items-center gap-8 mt-10 border-t border-slate-50 dark:border-white/5 pt-6 overflow-x-auto no-scrollbar">
                    {[
                        { id: 'PANEL', label: 'Monitor de Operaciones', icon: FiLayers },
                        { id: 'TAREAS', label: 'Cola de Tareas', icon: FiClipboard },
                        { id: 'INCIDENCIAS', label: 'Gestión de Incidencias', icon: FiAlertCircle },
                        { id: 'METRICAS', label: 'KPIs Operativos', icon: FiBarChart2 },
                    ].map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id as any)}
                            className={`flex items-center gap-2 text-xs font-black uppercase tracking-widest transition-all pb-4 border-b-2 ${
                                activeTab === tab.id
                                ? 'border-brand text-brand'
                                : 'border-transparent text-slate-400 hover:text-slate-600'
                            }`}
                        >
                            <tab.icon size={16} /> {tab.label}
                        </button>
                    ))}
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-8 space-y-8">
                {/* Modal de Nueva Operación */}
                {isNewOpModalOpen && (
                    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
                        <div className="bg-white dark:bg-slate-900 p-8 rounded-[2rem] shadow-2xl w-full max-w-2xl animate-in zoom-in-95 duration-300">
                            <h2 className="text-2xl font-black uppercase italic mb-6">Activar Operación desde Venta</h2>
                            <div className="space-y-6">
                                <div>
                                    <label className="text-[10px] font-black uppercase text-slate-400 mb-2 block">Ventas Pendientes de Ejecución</label>
                                    <div className="space-y-3">
                                        {[
                                            { id: 'FV-1026', client: 'Hotel Las Nubes', service: 'Pack Marketing Digital' },
                                            { id: 'FV-1027', client: 'Restaurante El Faro', service: 'Renovación de Menú' }
                                        ].map(sale => (
                                            <div
                                                key={sale.id}
                                                className="border border-slate-100 dark:border-white/5 p-4 rounded-xl flex justify-between items-center hover:bg-slate-50 dark:hover:bg-white/5 cursor-pointer group"
                                                onClick={() => {
                                                    alert(`Generando Operación para ${sale.id}. Descomponiendo servicio en 4 tareas automáticas...`);
                                                    setIsNewOpModalOpen(false);
                                                }}
                                            >
                                                <div>
                                                    <p className="font-bold text-slate-900 dark:text-white">{sale.service}</p>
                                                    <p className="text-xs text-slate-500">{sale.client} • {sale.id}</p>
                                                </div>
                                                <FiArrowRight className="text-brand group-hover:translate-x-1 transition-transform" />
                                            </div>
                                        ))}
                                    </div>
                                </div>
                                <div className="pt-6 border-t dark:border-white/5 flex justify-end gap-3">
                                    <Button variant="ghost" onClick={() => setIsNewOpModalOpen(false)}>Cancelar</Button>
                                    <Button className="bg-brand text-white font-black">Crear Manualmente</Button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'PANEL' && (
                    <ViewState
                        isLoading={isLoading}
                        isEmpty={operations.length === 0}
                        emptyMessage="Sin operaciones activas."
                    >
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-full">
                        {/* Lista de Operaciones Activas */}
                        <div className="lg:col-span-2 space-y-6">
                            <h3 className="text-sm font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
                                <div className="w-2 h-2 bg-brand rounded-full animate-pulse"></div> Órdenes Especializadas ({operations.length})
                            </h3>
                            <div className="grid grid-cols-1 gap-4">
                                {operations.map(op => (
                                    <Card
                                        key={op.id}
                                        className={`border-none shadow-sm cursor-pointer transition-all hover:shadow-md ${selectedOpId === op.id ? 'ring-2 ring-brand' : 'bg-white dark:bg-white/5'}`}
                                        onClick={() => setSelectedOpId(op.id)}
                                    >
                                        <CardContent className="p-6">
                                            <div className="flex justify-between items-start mb-4">
                                                <div>
                                                    <p className="text-[10px] font-black text-brand uppercase tracking-tighter mb-1">ORDEN {op.id?.slice(0,8)}</p>
                                                    <h4 className="text-xl font-bold text-slate-900 dark:text-white leading-tight">{op.descripcion_servicio}</h4>
                                                    <p className="text-sm text-slate-500 mt-1 flex items-center gap-1"><FiUser size={12}/> Contrato: {op.contrato_ref_id?.slice(0,8)}</p>
                                                </div>
                                                <Badge className={`uppercase font-black text-[10px] ${
                                                    op.estado === 'CONFIRMADA' ? 'bg-blue-100 text-blue-700' :
                                                    op.estado === 'COMPLETADA' ? 'bg-emerald-100 text-emerald-700' :
                                                    'bg-slate-100 text-slate-700'
                                                }`}>
                                                    {op.estado}
                                                </Badge>
                                            </div>

                                            <div className="mt-6 flex items-center justify-between border-t border-slate-50 dark:border-white/5 pt-4">
                                                <div className="text-[10px] font-black text-slate-400 flex items-center gap-1 uppercase">
                                                   <FiClock /> Inicio: {new Date(op.fecha_inicio).toLocaleDateString()}
                                                </div>
                                                <div className="text-[10px] font-black text-brand flex items-center gap-1 uppercase">
                                                   ${op.precio_total} COP
                                                </div>
                                            </div>
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        </div>

                        {/* Detalle de Operación Seleccionada */}
                        <div className="lg:col-span-1">
                            {selectedOp ? (
                                <div className="space-y-6 animate-in slide-in-from-right duration-500 sticky top-32">
                                    <div className="flex justify-between items-center">
                                        <h3 className="text-sm font-black text-slate-900 dark:text-white uppercase tracking-widest">Interoperabilidad Logística</h3>
                                        <button onClick={() => setSelectedOpId(null)} className="text-xs text-slate-400 hover:text-slate-900">Cerrar</button>
                                    </div>

                                    <Card className="border-none bg-slate-900 text-white shadow-xl rounded-3xl overflow-hidden">
                                        <CardContent className="p-8">
                                            <p className="text-indigo-400 text-[10px] font-black uppercase tracking-[0.2em] mb-4">Subórdenes Delivery</p>
                                            <div className="space-y-4">
                                                {selectedOp.related_deliveries?.map((del: any) => (
                                                   <div key={del.id} className="bg-white/5 p-4 rounded-2xl border border-white/5">
                                                      <div className="flex justify-between items-start mb-2">
                                                         <span className="text-[9px] font-black px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-400 uppercase tracking-widest">{del.status}</span>
                                                         <span className="text-[9px] text-slate-500 font-mono">{del.id.slice(0,8)}</span>
                                                      </div>
                                                      <p className="text-xs font-bold text-white mb-1">Destino: {del.destination_address}</p>
                                                      <p className="text-[10px] text-slate-400">Conductor: {del.driver?.username || 'Pendiente'}</p>
                                                   </div>
                                                ))}
                                                {selectedOp.related_deliveries?.length === 0 && (
                                                   <div className="text-center py-6 border-2 border-dashed border-white/10 rounded-2xl opacity-40">
                                                      <p className="text-[10px] font-black uppercase">Sin Logística Asignada</p>
                                                   </div>
                                                )}
                                            </div>

                                            <div className="mt-10 pt-6 border-t border-white/10 flex flex-col gap-3">
                                                <Button
 
                                                    className="w-full bg-brand text-white font-black text-xs py-6 rounded-2xl shadow-lg shadow-brand/20 hover:scale-[1.02] transition-transform flex items-center justify-center gap-2"
                                                    onClick={() => toast.info("Generando Suborden de Delivery via Puente Interoperable...")}
                                                >
                                                    <FiArrowRight /> Solicitar Delivery para Orden
 
                                                </Button>

                                                <div className="bg-white/5 p-4 rounded-2xl">
                                                   <p className="text-[9px] font-black uppercase text-indigo-400 mb-2">Sincronización ERP</p>
                                                   <div className="flex items-center gap-2 text-[10px] text-slate-400">
                                                      <FiCheckCircle className="text-emerald-500" /> Trazabilidad Quíntuple Activa
                                                   </div>
                                                </div>
                                            </div>
                                        </CardContent>
                                    </Card>
                                </div>
                            ) : (
                                <div className="h-[400px] border-2 border-dashed border-slate-200 dark:border-white/5 rounded-[2rem] flex flex-col items-center justify-center text-center p-8">
                                    <FiActivity size={48} className="text-slate-200 dark:text-white/10 mb-4" />
                                    <p className="text-slate-400 font-bold uppercase tracking-widest text-xs">Selecciona una operación para gestionar su ejecución</p>
                                </div>
                            )}
                        </div>
                    </div>
                    </ViewState>
                )}

                {activeTab === 'TAREAS' && (
                    <div className="animate-in fade-in duration-500">
                        <Card className="border-none shadow-sm bg-white dark:bg-white/5 overflow-hidden">
                            <CardHeader className="bg-slate-50 dark:bg-black/20 px-8 py-6">
                                <CardTitle className="text-sm font-black uppercase tracking-[0.2em]">Cola Maestra de Tareas</CardTitle>
                            </CardHeader>
                            <CardContent className="p-0">
                                <Table>
                                    <TableHeader>
                                        <TableRow className="border-slate-50 dark:border-white/5">
                                            <TableHead className="px-8 font-black text-[10px] uppercase">Tarea</TableHead>
                                            <TableHead className="font-black text-[10px] uppercase">Operación</TableHead>
                                            <TableHead className="font-black text-[10px] uppercase">Responsable</TableHead>
                                            <TableHead className="font-black text-[10px] uppercase text-center">Estado</TableHead>
                                            <TableHead className="px-8 text-right font-black text-[10px] uppercase">Acción</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {operations.flatMap(op => op.actividades.flatMap(act => act.tareas)).map(tarea => {
                                            const op = operations.find(o => o.actividades.some(a => a.tareas.some(t => t.id === tarea.id)));
                                            return (
                                                <TableRow key={tarea.id} className="border-slate-50 dark:border-white/5 hover:bg-slate-50 transition-colors">
                                                    <TableCell className="px-8">
                                                        <p className="font-bold text-sm">{tarea.nombre}</p>
                                                        <p className="text-[10px] text-slate-400 font-black uppercase tracking-tighter italic">Vence: {tarea.fecha_limite}</p>
                                                    </TableCell>
                                                    <TableCell className="text-xs font-medium text-slate-500">{op?.servicio_nombre}</TableCell>
                                                    <TableCell className="text-xs font-bold">{tarea.responsable}</TableCell>
                                                    <TableCell className="text-center">
                                                        <Badge className={`text-[9px] font-black uppercase ${
                                                            tarea.estado === 'LISTO' ? 'bg-emerald-100 text-emerald-700' :
                                                            tarea.estado === 'EN_PROGRESO' ? 'bg-blue-100 text-blue-700' :
                                                            'bg-slate-100 text-slate-700'
                                                        }`}>
                                                            {tarea.estado}
                                                        </Badge>
                                                    </TableCell>
                                                    <TableCell className="px-8 text-right">
                                                        <Button variant="ghost" size="sm" className="text-brand font-black hover:bg-brand/10">Gestionar</Button>
                                                    </TableCell>
                                                </TableRow>
                                            );
                                        })}
                                    </TableBody>
                                </Table>
                            </CardContent>
                        </Card>
                    </div>
                )}

                {activeTab === 'INCIDENCIAS' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-in slide-in-from-bottom-8 duration-500">
                        {operations.flatMap(op => op.incidencias.map(inc => ({ ...inc, opName: op.servicio_nombre, opId: op.id }))).map(inc => (
                            <Card key={inc.id} className="border-l-4 border-l-red-500 shadow-sm hover:shadow-xl transition-all group overflow-hidden bg-white">
                                <CardContent className="p-6">
                                    <div className="flex justify-between items-start mb-4">
                                        <Badge className={`text-[9px] font-black uppercase ${
                                            inc.prioridad === 'ALTA' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'
                                        }`}>{inc.prioridad} PRIORIDAD</Badge>
                                        <span className="text-[10px] font-black text-slate-400">{inc.fecha}</span>
                                    </div>
                                    <h4 className="font-bold text-slate-900 mb-2 leading-tight group-hover:text-red-600 transition-colors">{inc.titulo}</h4>
                                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-tighter italic mb-6">En Op: {inc.opName}</p>

                                    <div className="flex items-center justify-between mt-auto border-t border-slate-50 pt-4">
                                        <div className="flex items-center gap-2">
                                            <span className="text-[10px] font-black uppercase text-slate-500">Estado:</span>
                                            <span className={`text-[10px] font-black ${inc.estado === 'RESUELTA' ? 'text-emerald-600' : 'text-red-600 animate-pulse'}`}>{inc.estado}</span>
                                        </div>
                                        {inc.estado !== 'RESUELTA' && (
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                className="text-[9px] font-black h-8 rounded-lg border-red-100 text-red-600 hover:bg-red-50"
                                                onClick={() => resolveIncident(inc.opId, inc.id)}
                                            >
                                                Resolver
                                            </Button>
                                        )}
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                        {/* Botón para reportar nueva incidencia rápida */}
                        <Card className="border-2 border-dashed border-slate-200 flex items-center justify-center p-6 cursor-pointer hover:border-brand hover:bg-brand/5 transition-all group">
                             <div className="text-center">
                                <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto mb-3 group-hover:bg-brand group-hover:text-white transition-colors">
                                    <FiPlus size={24} />
                                </div>
                                <p className="text-[10px] font-black uppercase text-slate-400 group-hover:text-brand">Nueva Alerta</p>
                             </div>
                        </Card>
                    </div>
                )}

                {activeTab === 'METRICAS' && (
                    <div className="space-y-8 animate-in zoom-in-95 duration-500">
                         <div className="bg-amber-50 border border-amber-200 p-4 rounded-2xl flex items-center gap-3 text-sm text-amber-700 font-bold">
                            <FiAlertCircle size={20} />
                            <span>MODO DEMO: Los KPIs operativos se calculan en base a la ejecución simulada actual.</span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            {[
                                { label: 'Tiempos de Entrega', val: '4.2 días', change: '-12%', icon: FiClock, color: 'text-indigo-600' },
                                { label: 'Cumplimiento SLA', val: '94%', change: '+2.1%', icon: FiCheckCircle, color: 'text-emerald-600' },
                                { label: 'Incidencias / Op', val: '0.8', change: '+5%', icon: FiAlertCircle, color: 'text-red-600' },
                                { label: 'Eficiencia Operador', val: '8.4', change: '+1.0', icon: FiTrendingUp, color: 'text-blue-600' },
                            ].map((kpi, i) => (
                                <Card key={i} className="border-none shadow-sm bg-white p-8">
                                    <div className="flex justify-between items-start mb-4">
                                        <div className={`p-3 rounded-2xl bg-slate-50 ${kpi.color}`}>
                                            <kpi.icon size={20} />
                                        </div>
                                        <span className={`text-xs font-black ${kpi.change.startsWith('+') ? 'text-emerald-500' : 'text-red-500'}`}>{kpi.change}</span>
                                    </div>
                                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">{kpi.label}</p>
                                    <h3 className="text-3xl font-black text-slate-900">{kpi.val}</h3>
                                </Card>
                            ))}
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                            <Card className="border-none shadow-sm bg-white p-8">
                                <CardTitle className="text-sm font-black uppercase tracking-widest mb-8 flex items-center justify-between">
                                    Carga por Responsable
                                    <FiUsers className="text-slate-300" />
                                </CardTitle>
                                <div className="space-y-6">
                                    {[
                                        { name: 'Carlos Operador', load: 85, color: 'bg-red-500', status: 'Saturado' },
                                        { name: 'Ana Soporte', load: 40, color: 'bg-emerald-500', status: 'Ligero' },
                                        { name: 'Luis Guía', load: 60, color: 'bg-amber-500', status: 'Normal' },
                                    ].map((user, i) => (
                                        <div key={i} className="space-y-2">
                                            <div className="flex justify-between text-xs font-bold">
                                                <span>{user.name}</span>
                                                <span className={`uppercase text-[9px] font-black ${
                                                    user.status === 'Saturado' ? 'text-red-500' :
                                                    user.status === 'Normal' ? 'text-amber-500' : 'text-emerald-500'
                                                }`}>{user.status}</span>
                                            </div>
                                            <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                                                <div className={`h-full ${user.color}`} style={{ width: `${user.load}%` }}></div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </Card>

                            <Card className="border-none shadow-sm bg-slate-50 dark:bg-white/5 p-8">
                                <CardTitle className="text-sm font-black uppercase tracking-widest mb-8 flex items-center justify-between">
                                    Satisfacción del Cliente (Post-Operación)
                                    <FiCheckCircle className="text-emerald-500" />
                                </CardTitle>
                                <div className="flex items-center gap-6">
                                    <div className="text-5xl font-black text-slate-900 dark:text-white">4.8</div>
                                    <div className="flex-1 space-y-2">
                                        <div className="flex gap-1 text-amber-400">
                                            {[1,2,3,4,5].map(i => <FiPlus key={i} size={16} fill="currentColor"/>)}
                                        </div>
                                        <p className="text-xs text-slate-500 font-bold uppercase">Basado en 24 calificaciones recientes.</p>
                                    </div>
                                </div>
                                <div className="mt-8 pt-8 border-t border-slate-100 dark:border-white/5 space-y-4">
                                     <div className="flex justify-between items-center text-xs">
                                         <span className="font-medium text-slate-500 italic">"Excelente coordinación en el tour llanero."</span>
                                         <Badge className="bg-emerald-100 text-emerald-700 text-[8px]">5.0</Badge>
                                     </div>
                                </div>
                            </Card>

                            <Card className="border-none shadow-sm bg-slate-900 text-white p-8 overflow-hidden relative lg:col-span-2">
                                <div className="absolute -right-10 -bottom-10 opacity-10">
                                    <FiActivity size={200} />
                                </div>
                                <h3 className="text-xl font-bold mb-4 italic">Análisis de Cuellos de Botella</h3>
                                <p className="text-slate-400 text-sm mb-8 leading-relaxed">He detectado que la actividad de "Reserva de Transporte" está bloqueando el 30% de tus nuevas operaciones. Recomiendo automatizar este paso mediante la integración directa con la flota de transporte.</p>
                                <Button className="bg-brand text-white font-black text-xs px-8 py-4 rounded-xl">Ver Plan de Mejora</Button>
                            </Card>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
