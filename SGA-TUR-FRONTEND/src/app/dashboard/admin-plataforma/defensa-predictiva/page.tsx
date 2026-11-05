'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import {
  FiZap, FiActivity, FiAlertCircle, FiCpu, FiLock, FiTrendingUp, FiTarget, FiShield
} from 'react-icons/fi';
import { ViewState } from '@/components/ui/ViewState';
import api from '@/services/api';
import { toast } from 'react-hot-toast';

interface Scenario {
    id: string;
    title: string;
    attack_vector: string;
    probability: number;
    estimated_impact: string;
    is_active_threat: boolean;
}

interface Action {
    id: string;
    action_name: string;
    target_node_name: string;
    explanation: string;
    is_applied: boolean;
}

export default function PredictiveDefensePanel() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [actions, setActions] = useState<Action[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPredictiveData();
  }, []);

  const fetchPredictiveData = async () => {
    setIsLoading(true);
    setError(null);
    try {
        // En F-CF/S-2 conectamos a los nuevos endpoints predictivos
        const [scRes, actRes] = await Promise.all([
            api.get('/admin/plataforma/defense-predictive/scenarios/'),
            api.get('/admin/plataforma/defense-predictive/hardening-actions/')
        ]);
        setScenarios(scRes.data.results || []);
        setActions(actRes.data.results || []);
    } catch (err: any) {
        console.error("PDE fetch error:", err);
        setError("FALLO PREDICTIVO: El motor PDE no responde. La anticipación estratégica ha sido suspendida.");
    } finally {
        setIsLoading(false);
    }
  };

  const getProbabilityBadge = (prob: number) => {
    const p = prob * 100;
    if (p > 80) return <Badge className="bg-red-600 text-white animate-pulse">CRÍTICA ({p}%)</Badge>;
    if (p > 50) return <Badge className="bg-orange-500 text-white">ALTA ({p}%)</Badge>;
    if (p > 20) return <Badge className="bg-amber-100 text-amber-700">MEDIA ({p}%)</Badge>;
    return <Badge className="bg-slate-100 text-slate-700">BAJA ({p}%)</Badge>;
  };

  return (
    <ViewState isLoading={isLoading} error={error}>
      <div className="space-y-10 animate-in fade-in duration-700">
        {/* Header Predictivo */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-gray-100 pb-8">
            <div>
                <div className="flex items-center gap-3 mb-2">
                    <div className="bg-indigo-900 text-white p-2 rounded-lg shadow-lg shadow-indigo-500/20">
                        <FiZap size={24} />
                    </div>
                    <h1 className="text-4xl font-black text-slate-900 tracking-tighter uppercase italic">Análisis Predictivo de Riesgos</h1>
                </div>
                <p className="text-slate-500 text-lg font-medium italic">"El mejor ataque es el que nunca alcanza a ejecutarse." — Doctrina S-2</p>
            </div>
            <div className="flex gap-4">
                <div className="px-6 py-3 bg-indigo-50 border border-indigo-100 rounded-2xl flex items-center gap-3">
                    <div className="w-3 h-3 bg-indigo-500 rounded-full animate-pulse" />
                    <span className="text-sm font-black text-indigo-700 tracking-widest uppercase">Motor PDE Activo</span>
                </div>
                <Button variant="outline" className="rounded-2xl border-slate-200 text-slate-600 font-bold px-6">
                    Simular Ataque
                </Button>
            </div>
        </div>

        {/* Global Threat Level */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card className="border-none shadow-sm bg-white p-8 overflow-hidden relative">
                <div className="absolute right-[-20px] bottom-[-20px] opacity-5">
                    <FiTrendingUp size={160} />
                </div>
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Nivel de Amenaza Proyectado (24h)</p>
                <h3 className="text-5xl font-black text-emerald-600 italic">BAJO</h3>
                <p className="text-xs text-slate-500 mt-4 flex items-center gap-1">
                    <FiActivity size={12} /> Basado en 42,000 señales sensoriales.
                </p>
            </Card>

            <Card className="border-none shadow-sm bg-white p-8">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Zonas Calientes (Superficie)</p>
                <div className="space-y-4">
                    <div className="flex justify-between items-center">
                        <span className="text-sm font-bold text-slate-700">Endpoints Públicos</span>
                        <Badge className="bg-red-100 text-red-700">35% RIESGO</Badge>
                    </div>
                    <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                        <div className="h-full bg-red-500 w-[35%]" />
                    </div>
                    <div className="flex justify-between items-center pt-2">
                        <span className="text-sm font-bold text-slate-700">Agentes Operativos</span>
                        <Badge className="bg-emerald-100 text-emerald-700">5% RIESGO</Badge>
                    </div>
                    <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                        <div className="h-full bg-emerald-500 w-[5%]" />
                    </div>
                </div>
            </Card>

            <Card className="border-none shadow-xl bg-slate-900 text-white p-8 rounded-[2rem] flex flex-col justify-between">
                <div>
                    <FiShield className="text-indigo-400 mb-4" size={32} />
                    <h4 className="text-xl font-black italic">Gobernanza PDE</h4>
                    <p className="text-slate-400 text-sm mt-2">Nivel de autonomía actual: <span className="text-white font-bold">PROPOSITIVO (S-1.5)</span></p>
                </div>
                <Button className="mt-6 bg-indigo-600 hover:bg-indigo-700 text-white font-black text-xs uppercase tracking-widest py-3 rounded-xl">
                    Ajustar Umbrales
                </Button>
            </Card>
        </div>

        {/* Scenarios & Hardening Table */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <Card className="border-none shadow-sm bg-white rounded-[2.5rem] overflow-hidden">
                <CardHeader className="p-10 border-b border-slate-50 flex flex-row items-center justify-between bg-slate-50/30">
                    <CardTitle className="text-xl font-black uppercase tracking-widest flex items-center gap-3 italic">
                        <FiTarget className="text-orange-500" /> Escenarios Anticipados (PDE)
                    </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead className="px-10 py-6 font-black uppercase text-[10px]">Escenario / Vector</TableHead>
                                <TableHead className="font-black uppercase text-[10px]">Probabilidad</TableHead>
                                <TableHead className="font-black uppercase text-[10px] text-right px-10">Impacto</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {scenarios.length === 0 ? (
                                <TableRow><TableCell colSpan={3} className="p-20 text-center text-slate-400 uppercase italic text-xs">No hay escenarios predictivos activos.</TableCell></TableRow>
                            ) : scenarios.map(s => (
                                <TableRow key={s.id}>
                                    <TableCell className="px-10 py-8">
                                        <p className="font-black text-slate-900 uppercase italic">{s.title}</p>
                                        <p className="text-[10px] text-slate-400 uppercase tracking-widest">{s.attack_vector}</p>
                                    </TableCell>
                                    <TableCell>{getProbabilityBadge(s.probability)}</TableCell>
                                    <TableCell className="text-right px-10 font-black text-xs uppercase text-slate-600">{s.estimated_impact}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            <Card className="border-none shadow-sm bg-white rounded-[2.5rem] overflow-hidden">
                <CardHeader className="p-10 border-b border-slate-50 flex flex-row items-center justify-between bg-slate-50/30">
                    <CardTitle className="text-xl font-black uppercase tracking-widest flex items-center gap-3 italic">
                        <FiLock className="text-indigo-600" /> Endurecimiento Proactivo
                    </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead className="px-10 py-6 font-black uppercase text-[10px]">Acción Preventiva</TableHead>
                                <TableHead className="font-black uppercase text-[10px]">Estado</TableHead>
                                <TableHead className="font-black uppercase text-[10px] text-right px-10">Target</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {actions.length === 0 ? (
                                <TableRow><TableCell colSpan={3} className="p-20 text-center text-slate-400 uppercase italic text-xs">No hay medidas preventivas aplicadas.</TableCell></TableRow>
                            ) : actions.map(a => (
                                <TableRow key={a.id} className={a.is_applied ? "bg-emerald-50/30" : ""}>
                                    <TableCell className="px-10 py-8">
                                        <p className="font-black text-slate-900 uppercase italic">{a.action_name}</p>
                                        <p className="text-xs text-slate-500 italic mt-1 max-w-[200px] leading-tight">"{a.explanation}"</p>
                                    </TableCell>
                                    <TableCell>
                                        {a.is_applied ?
                                            <Badge className="bg-emerald-500 text-white font-black text-[9px]">APLICADA</Badge> :
                                            <Badge variant="outline" className="text-[9px] font-black">PROPUESTA</Badge>
                                        }
                                    </TableCell>
                                    <TableCell className="text-right px-10">
                                        <span className="text-[10px] font-mono text-indigo-600 bg-indigo-50 px-2 py-1 rounded">{a.target_node_name}</span>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>

        {/* Simulación Red Team Sandbox (S-2.3) */}
        <Card className="border-none shadow-sm bg-slate-50 border border-slate-200 rounded-[2rem] p-10">
            <div className="flex items-center gap-6">
                <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center shadow-md">
                    <FiCpu className="text-slate-400" size={32} />
                </div>
                <div>
                    <h3 className="text-2xl font-black text-slate-900 uppercase italic">Sandbox de Simulación Adversarial</h3>
                    <p className="text-slate-500 mt-2">La IA está ejecutando 12 variantes de ataque en el entorno aislado para predecir fallos de lógica.</p>
                </div>
                <div className="flex-1"></div>
                <div className="text-right">
                    <p className="text-[10px] font-black text-slate-400 uppercase mb-1">Carga Virtual</p>
                    <p className="text-2xl font-black text-indigo-600">84%</p>
                </div>
            </div>
        </Card>
      </div>
    </ViewState>
  );
}
