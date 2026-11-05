'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import {
  FiTarget, FiGhost, FiActivity, FiShield, FiCpu, FiUserX, FiBarChart2, FiLayers
} from 'react-icons/fi';
import { ViewState } from '@/components/ui/ViewState';
import api from '@/services/api';
import { toast } from 'react-hot-toast';

interface Adversary {
    id: string;
    source_ip: string;
    technical_level: string;
    persistence_score: number;
    is_quarantined: boolean;
}

interface GhostSurface {
    id: string;
    name: string;
    path: string;
    deception_type: string;
    is_active: boolean;
}

export default function DefensiveIntelligencePanel() {
  const [adversaries, setAdversaries] = useState<Adversary[]>([]);
  const [surfaces, setSurfaces] = useState<GhostSurface[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchIntelligenceData();
  }, []);

  const fetchIntelligenceData = async () => {
    setIsLoading(true);
    setError(null);
    try {
        const [advRes, surfRes, statRes] = await Promise.all([
            api.get('/admin/plataforma/defense-deception/adversaries/'),
            api.get('/admin/plataforma/defense-deception/ghost-surfaces/'),
            api.get('/admin/plataforma/defense-deception/stats/')
        ]);
        setAdversaries(advRes.data.results || []);
        setSurfaces(surfRes.data.results || []);
        setStats(statRes.data);
    } catch (err: any) {
        console.error("ADL fetch error:", err);
        setError("FALLO ESTRATÉGICO: No se pudo sincronizar con la Capa de Engaño Adaptativo (ADL).");
    } finally {
        setIsLoading(false);
    }
  };

  return (
    <ViewState isLoading={isLoading} error={error}>
      <div className="space-y-10 animate-in fade-in duration-700">
        {/* Header S-3 */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-gray-100 pb-8">
            <div>
                <div className="flex items-center gap-3 mb-2">
                    <div className="bg-orange-900 text-white p-2 rounded-lg shadow-lg">
                        <FiTarget size={24} />
                    </div>
                    <h1 className="text-4xl font-black text-slate-900 tracking-tighter uppercase italic">Inteligencia Defensiva y Disuasión</h1>
                </div>
                <p className="text-slate-500 text-lg font-medium italic">"Convencer al adversario de que no vale la pena golpear." — Doctrina S-3</p>
            </div>
            <div className="flex gap-4">
                <div className="px-6 py-3 bg-orange-50 border border-orange-100 rounded-2xl flex items-center gap-3">
                    <div className="w-3 h-3 bg-orange-500 rounded-full animate-pulse" />
                    <span className="text-sm font-black text-orange-700 tracking-widest uppercase">Capa ADL Activa</span>
                </div>
                <Button className="bg-slate-900 text-white font-black px-8 py-6 rounded-2xl shadow-xl shadow-slate-500/20">
                    Nueva Superficie Fantasma
                </Button>
            </div>
        </div>

        {/* Intelligence Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card className="border-none shadow-sm bg-white p-8">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Intentos Disuadidos (ROI Atacante 0)</p>
                <h3 className="text-5xl font-black text-slate-900">{stats?.total_dissuaded_attempts || 0}</h3>
                <div className="mt-4 flex items-center gap-1 text-xs text-emerald-600 font-bold">
                    <FiActivity size={12} /> Neutralización silenciosa activa.
                </div>
            </Card>

            <Card className="border-none shadow-sm bg-white p-8">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Tiempo Perdido por Adversarios</p>
                <h3 className="text-5xl font-black text-orange-600 italic">{stats?.avg_abandonment_time_minutes || 0}m</h3>
                <p className="text-xs text-slate-500 mt-4 flex items-center gap-1">
                    <FiLayers size={12} /> Drenaje de ataque mediante fricción.
                </p>
            </Card>

            <Card className="border-none shadow-sm bg-white p-8">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Costo Cognitivo Impuesto</p>
                <h3 className="text-5xl font-black text-indigo-600">{stats?.total_cognitive_cost_imposed || 0}</h3>
                <p className="text-xs text-slate-500 mt-4">Unidad de medida de ineficacia adversarial.</p>
            </Card>
        </div>

        {/* Ghost Surfaces Map */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <Card className="lg:col-span-2 border-none shadow-sm bg-white rounded-[2.5rem] overflow-hidden">
                <CardHeader className="p-10 border-b border-slate-50 flex flex-row items-center justify-between bg-slate-50/30">
                    <CardTitle className="text-xl font-black uppercase tracking-widest flex items-center gap-3 italic">
                        <FiGhost className="text-indigo-500" /> Superficies Fantasma Activas (S-3.1)
                    </CardTitle>
                    <Badge className="bg-indigo-100 text-indigo-700 font-black">ENTORNO DE ENGAÑO</Badge>
                </CardHeader>
                <CardContent className="p-0">
                    <Table>
                        <TableHeader className="bg-slate-900 text-white">
                            <TableRow>
                                <TableHead className="px-10 py-6 font-black uppercase text-[10px]">Superficie / Path</TableHead>
                                <TableHead className="font-black uppercase text-[10px]">Tipo de Engaño</TableHead>
                                <TableHead className="font-black uppercase text-[10px] text-right px-10">Estado</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {surfaces.map(s => (
                                <TableRow key={s.id} className="hover:bg-slate-50 transition-all border-slate-100">
                                    <TableCell className="px-10 py-8">
                                        <p className="font-black text-slate-900 uppercase italic">{s.name}</p>
                                        <p className="text-[10px] font-mono text-slate-400">{s.path}</p>
                                    </TableCell>
                                    <TableCell>
                                        <Badge variant="outline" className="font-black text-[9px]">{s.deception_type}</Badge>
                                    </TableCell>
                                    <TableCell className="text-right px-10">
                                        <div className="flex items-center justify-end gap-2">
                                            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                                            <span className="text-[10px] font-black uppercase">PROTEGIENDO</span>
                                        </div>
                                    </TableCell>
                                </TableRow>
                            ))}
                            {surfaces.length === 0 && (
                                <TableRow><TableCell colSpan={3} className="p-20 text-center text-slate-400 uppercase italic text-xs">No hay superficies de engaño configuradas.</TableCell></TableRow>
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            <div className="space-y-8">
                {/* Adversary Profiles */}
                <Card className="border-none shadow-xl bg-slate-900 text-white rounded-[2rem] p-8">
                    <h4 className="text-xl font-black italic flex items-center gap-2 mb-6">
                        <FiUserX className="text-red-400" /> Perfiles Hostiles (S-3.4)
                    </h4>
                    <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                        {adversaries.map(a => (
                            <div key={a.id} className="p-4 bg-white/5 rounded-2xl border border-white/10 flex flex-col gap-3">
                                <div className="flex justify-between items-center">
                                    <span className="text-[10px] font-mono text-indigo-400">{a.source_ip}</span>
                                    <Badge className="bg-red-500/20 text-red-400 border-red-500/30 text-[8px]">NEUTRALIZADO</Badge>
                                </div>
                                <div className="flex justify-between items-end">
                                    <div>
                                        <p className="text-[9px] font-black text-slate-500 uppercase">Nivel Técnico</p>
                                        <p className="text-sm font-bold">{a.technical_level}</p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-[9px] font-black text-slate-500 uppercase">Persistencia</p>
                                        <p className="text-sm font-bold text-orange-400">{(a.persistence_score * 100).toFixed(0)}%</p>
                                    </div>
                                </div>
                            </div>
                        ))}
                        {adversaries.length === 0 && (
                            <p className="text-center text-slate-500 uppercase italic text-[10px] py-10">Sin perfiles hostiles capturados.</p>
                        )}
                    </div>
                </Card>

                <Card className="border-none shadow-sm bg-white p-8 rounded-[2rem]">
                    <h4 className="text-sm font-black uppercase tracking-widest mb-6 flex items-center gap-2">
                        <FiShield className="text-brand" /> Neutralización No Coercitiva
                    </h4>
                    <p className="text-xs text-slate-500 leading-relaxed mb-6 italic">
                        "El sistema redirecciona la actividad sospechosa a una burbuja inerte sin confrontación directa, agotando los recursos del atacante."
                    </p>
                    <div className="space-y-4">
                        <div className="flex justify-between items-center text-[10px] font-black uppercase text-slate-400">
                            <span>Fricción Estratégica</span>
                            <span className="text-slate-900">ACTIVA</span>
                        </div>
                        <div className="h-1 bg-slate-100 rounded-full">
                            <div className="h-full bg-brand w-[80%]" />
                        </div>
                    </div>
                </Card>
            </div>
        </div>
      </div>
    </ViewState>
  );
}
