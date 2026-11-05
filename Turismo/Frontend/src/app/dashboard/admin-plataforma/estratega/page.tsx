"use client";

import React from 'react';
import useSWR from 'swr';
import api from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { FiZap, FiCheckCircle, FiXCircle, FiTrendingUp, FiCpu, FiMessageSquare } from 'react-icons/fi';
import { toast } from 'react-hot-toast';

export default function EstrategaPage() {
    const { data: proposals, mutate } = useSWR('/v1/enterprise-core/proposals/', (url) => api.get(url).then(res => res.data.data));

    const handleExecute = async (id: string) => {
        try {
            await api.post(`/v1/enterprise-core/proposals/${id}/execute/`);
            toast.success("Decisión ejecutada bajo mandato soberano.");
            mutate();
        } catch (e) {
            toast.error("Ejecución rechazada por el Kernel de Gobernanza.");
        }
    };

    return (
        <div className="p-8 space-y-10">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-4xl font-black text-slate-900 tracking-tighter uppercase italic">Estratega EOS: Cerebro IA</h1>
                    <p className="text-slate-500 font-medium italic">Visibilidad total sobre decisiones autónomas y propuestas tácticas.</p>
                </div>
                <div className="bg-indigo-600 text-white px-6 py-3 rounded-2xl font-black uppercase tracking-widest flex items-center gap-2">
                    <FiCpu className="animate-spin-slow" /> Inteligencia Nivel 3 Activa
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Panel de Propuestas */}
                <Card className="lg:col-span-2 border-none shadow-sm overflow-hidden">
                    <CardHeader className="bg-slate-50 border-b p-6">
                        <CardTitle className="text-xl font-black uppercase flex items-center gap-2">
                            <FiZap className="text-amber-500" /> Bitácora de Decisiones
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-0">
                        <div className="divide-y divide-slate-100">
                            {proposals?.length === 0 ? (
                                <div className="p-20 text-center text-slate-400 italic">No se han generado propuestas estratégicas en este ciclo.</div>
                            ) : proposals?.map((p: any) => (
                                <div key={p.id} className="p-8 hover:bg-slate-50 transition-colors">
                                    <div className="flex justify-between items-start mb-4">
                                        <div className="flex items-center gap-2">
                                            <Badge className={p.autonomy_level_applied === 3 ? "bg-indigo-600" : "bg-slate-200 text-slate-700"}>
                                                Lvl {p.autonomy_level_applied}
                                            </Badge>
                                            <span className="text-xs font-black uppercase tracking-widest text-slate-400">{p.agent_id}</span>
                                        </div>
                                        <Badge className={
                                            p.governance_status === 'EXECUTED' ? "bg-emerald-500" :
                                            p.governance_status === 'FAILED' ? "bg-red-500" : "bg-amber-500"
                                        }>
                                            {p.governance_status}
                                        </Badge>
                                    </div>
                                    <h3 className="text-xl font-bold text-slate-900 mb-2">{p.suggested_action.intention}</h3>
                                    <p className="text-slate-500 text-sm mb-2">Métrica disparadora: <span className="font-mono font-bold">{p.origin_metric}</span> ({p.metric_value})</p>

                                    <div className="bg-amber-50/50 p-4 rounded-xl mb-6 border border-amber-100">
                                        <p className="text-xs font-black text-amber-700 uppercase tracking-widest mb-1">Razonamiento IA</p>
                                        <p className="text-sm text-slate-700 italic">"Se detectó una desviación del {((parseFloat(p.metric_value)/10)-1)*100}% respecto al baseline. Se recomienda {p.suggested_action.intention} para estabilizar la rentabilidad del tenant."</p>
                                    </div>

                                    {p.governance_status === 'PENDING' && (
                                        <div className="flex gap-4">
                                            <Button onClick={() => handleExecute(p.id)} className="bg-slate-900 text-white font-black px-6">
                                                Validar y Ejecutar
                                            </Button>
                                            <Button variant="outline" className="border-red-100 text-red-500 hover:bg-red-50">
                                                Rechazar
                                            </Button>
                                        </div>
                                    )}

                                    {p.execution_result && (
                                        <div className="mt-4 p-4 bg-slate-50 rounded-xl font-mono text-[10px] text-slate-600">
                                            {JSON.stringify(p.execution_result)}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>

                {/* Sidebar de Inteligencia */}
                <div className="space-y-8">
                    <Card className="border-none shadow-xl bg-slate-900 text-white rounded-3xl overflow-hidden">
                        <CardHeader className="p-8 border-b border-white/10">
                            <CardTitle className="text-xl font-black flex items-center gap-2 italic">
                                <FiTrendingUp className="text-emerald-400" /> ROI de Inteligencia
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="p-8">
                            <div className="space-y-6">
                                <div>
                                    <p className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 mb-1">Ahorro Estimado (Mes)</p>
                                    <h3 className="text-3xl font-black">$4.2M</h3>
                                </div>
                                <div>
                                    <p className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 mb-1">Decisiones Autónomas</p>
                                    <h3 className="text-3xl font-black">124</h3>
                                </div>
                                <div className="pt-4 border-t border-white/5">
                                    <p className="text-xs text-slate-400 italic">"La IA ha optimizado el 12% de las compras recurrentes este mes."</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="border-none shadow-sm bg-white rounded-3xl">
                        <CardHeader className="p-8 border-b">
                            <CardTitle className="text-lg font-black uppercase tracking-tighter">Feedback Directivo</CardTitle>
                        </CardHeader>
                        <CardContent className="p-8">
                            <p className="text-sm text-slate-500 mb-6 font-medium">Ayuda al motor de aprendizaje calificando las acciones de los agentes.</p>
                            <Button className="w-full justify-between py-6 px-6 rounded-2xl bg-indigo-50 text-indigo-600 hover:bg-indigo-100 transition-all group border-none">
                                <span className="font-black text-xs uppercase tracking-widest">Ver solicitudes pendientes</span>
                                <FiMessageSquare size={20} />
                            </Button>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
