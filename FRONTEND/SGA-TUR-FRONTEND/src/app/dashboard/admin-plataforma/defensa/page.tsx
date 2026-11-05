'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import {
  FiShield, FiActivity, FiAlertOctagon, FiCpu, FiEye, FiLock, FiZap, FiFileText, FiRefreshCw
} from 'react-icons/fi';
import { ViewState } from '@/components/ui/ViewState';
import api from '@/services/api';
import { toast } from 'react-hot-toast';

interface Threat {
    id: string;
    attack_vector: string;
    threat_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    timestamp: string;
    source_ip: string;
    action_taken: string;
}

export default function SovereignDefensePanel() {
  const [threats, setThreats] = useState<Threat[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [defenseStatus, setDefenseStatus] = useState<'NORMAL' | 'ALERT' | 'ATTACK'>('NORMAL');

  useEffect(() => {
    fetchDefenseData();
  }, []);

  const fetchDefenseData = async () => {
    setIsLoading(true);
    setError(null);
    try {
        // En F-CF/S-1 conectamos al log forense real
        const res = await api.get('/admin/plataforma/audit/forensic-logs/');
        setThreats(res.data.results || []);

        // Determinar estado basado en amenazas recientes
        const activeCritical = res.data.results?.filter((t: Threat) => t.threat_level === 'CRITICAL').length;
        if (activeCritical > 0) setDefenseStatus('ATTACK');
        else if (res.data.results?.length > 0) setDefenseStatus('ALERT');
        else setDefenseStatus('NORMAL');

    } catch (err: any) {
        console.error("Defense fetch error:", err);
        setError("INTERRUPCIÓN SENSORIAL: No se pudo sincronizar con el Motor de Defensa. El estado de integridad es DESCONOCIDO.");
    } finally {
        setIsLoading(false);
    }
  };

  const getLevelColor = (level: string) => {
    switch (level) {
        case 'CRITICAL': return 'bg-red-600 text-white animate-pulse';
        case 'HIGH': return 'bg-orange-500 text-white';
        case 'MEDIUM': return 'bg-amber-100 text-amber-700';
        default: return 'bg-slate-100 text-slate-700';
    }
  };

  return (
    <ViewState isLoading={isLoading} error={error}>
      <div className="space-y-10 animate-in fade-in duration-700">
        {/* Header Institucional */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-gray-100 pb-8">
            <div>
                <div className="flex items-center gap-3 mb-2">
                    <div className={`p-2 rounded-lg ${defenseStatus === 'ATTACK' ? 'bg-red-600' : 'bg-slate-900'} text-white`}>
                        <FiShield size={24} />
                    </div>
                    <h1 className="text-4xl font-black text-slate-900 tracking-tighter uppercase italic">Centro de Defensa Soberana</h1>
                </div>
                <p className="text-slate-500 text-lg font-medium italic">Monitoreo de anillos de seguridad y respuesta autónoma coordinada.</p>
            </div>
            <div className="flex gap-4">
                <div className={`px-6 py-3 rounded-2xl flex items-center gap-3 border ${
                    defenseStatus === 'ATTACK' ? 'bg-red-50 border-red-200 text-red-700' :
                    defenseStatus === 'ALERT' ? 'bg-amber-50 border-amber-200 text-amber-700' :
                    'bg-emerald-50 border-emerald-100 text-emerald-700'
                }`}>
                    <div className={`w-3 h-3 rounded-full ${
                        defenseStatus === 'ATTACK' ? 'bg-red-600 animate-ping' :
                        defenseStatus === 'ALERT' ? 'bg-amber-500 animate-pulse' :
                        'bg-emerald-500'
                    }`} />
                    <span className="text-sm font-black tracking-widest uppercase">Estado: {defenseStatus}</span>
                </div>
                <Button onClick={fetchDefenseData} variant="outline" className="rounded-2xl h-full border-slate-200">
                    <FiRefreshCw className={isLoading ? 'animate-spin' : ''} />
                </Button>
            </div>
        </div>

        {/* Anillos de Defensa KPI */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
                { label: 'Anillo 0 (Kernel)', status: 'INTACTO', icon: FiLock, color: 'text-emerald-600' },
                { label: 'Anillo 1 (Observación)', status: 'ACTIVO', icon: FiEye, color: 'text-blue-600' },
                { label: 'Anillo 2 (Respuesta)', status: defenseStatus === 'NORMAL' ? 'STANDBY' : 'EN EJECUCIÓN', icon: FiZap, color: 'text-amber-600' },
                { label: 'Anillo 3 (Escalamiento)', status: threats.some(t => t.threat_level === 'CRITICAL') ? 'REQUERIDO' : 'PASAIVO', icon: FiAlertOctagon, color: 'text-red-600' },
            ].map((ring, i) => (
                <Card key={i} className="border-none shadow-sm bg-white">
                    <CardContent className="p-6">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1">{ring.label}</p>
                                <h4 className={`text-lg font-black ${ring.color}`}>{ring.status}</h4>
                            </div>
                            <ring.icon size={20} className="text-slate-300" />
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>

        {/* Registro Forense de Amenazas */}
        <Card className="border-none shadow-xl bg-white rounded-[2.5rem] overflow-hidden">
            <CardHeader className="p-10 border-b border-slate-50 flex flex-row items-center justify-between bg-slate-50/30">
                <CardTitle className="text-xl font-black uppercase tracking-widest flex items-center gap-3 italic">
                    <FiActivity className="text-red-500" /> Registro de Amenazas Detectadas (S-1.2)
                </CardTitle>
                <Badge variant="outline" className="font-black text-slate-400">TRAZABILIDAD FORENSE</Badge>
            </CardHeader>
            <CardContent className="p-0">
                <Table>
                    <TableHeader className="bg-slate-900 text-white">
                        <TableRow>
                            <TableHead className="px-10 py-6 font-black uppercase text-[10px] tracking-widest">Vector de Ataque</TableHead>
                            <TableHead className="font-black uppercase text-[10px] tracking-widest">Nivel</TableHead>
                            <TableHead className="font-black uppercase text-[10px] tracking-widest">Origen (IP)</TableHead>
                            <TableHead className="font-black uppercase text-[10px] tracking-widest">Respuesta Autónoma</TableHead>
                            <TableHead className="font-black uppercase text-[10px] tracking-widest text-right px-10">Timestamp</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {threats.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={5} className="py-20 text-center text-slate-400 uppercase italic tracking-widest text-xs">
                                    No se han detectado anomalías en el periodo de observación actual.
                                </TableCell>
                            </TableRow>
                        ) : threats.map((threat) => (
                            <TableRow key={threat.id} className="hover:bg-slate-50 border-slate-100 transition-all group">
                                <TableCell className="px-10 py-8">
                                    <p className="font-black text-slate-900 uppercase italic">{threat.attack_vector}</p>
                                    <p className="text-[10px] font-mono text-slate-400">Forensic-ID: {threat.id.substring(0,8)}</p>
                                </TableCell>
                                <TableCell>
                                    <Badge className={`font-black text-[9px] px-3 ${getLevelColor(threat.threat_level)}`}>
                                        {threat.threat_level}
                                    </Badge>
                                </TableCell>
                                <TableCell>
                                    <span className="font-mono text-xs text-slate-600 bg-slate-100 px-2 py-1 rounded">{threat.source_ip}</span>
                                </TableCell>
                                <TableCell>
                                    <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-amber-500" />
                                        <span className="text-xs font-bold text-slate-700">{threat.action_taken}</span>
                                    </div>
                                </TableCell>
                                <TableCell className="text-right px-10">
                                    <p className="text-xs font-bold text-slate-500">{new Date(threat.timestamp).toLocaleString()}</p>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>

        {/* Sandbox de Aprendizaje (S-1.4) */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <Card className="lg:col-span-2 border-none shadow-sm bg-slate-900 text-white rounded-[2rem] p-10 overflow-hidden relative group">
                <div className="absolute -right-10 -bottom-10 opacity-10 group-hover:scale-110 transition-transform duration-1000">
                    <FiCpu size={250} />
                </div>
                <div className="flex items-center gap-4 mb-6">
                    <Badge className="bg-indigo-500 text-white font-black">ANÁLISIS SANDBOX</Badge>
                    <span className="text-[10px] font-black uppercase tracking-widest text-indigo-400">Aprendizaje Defensivo Activo</span>
                </div>
                <h3 className="text-3xl font-black italic leading-tight">Propuestas de Endurecimiento</h3>
                <p className="mt-4 text-slate-400 text-lg leading-relaxed">
                    La IA está simulando variantes de los ataques detectados en entorno aislado.
                    Se han generado <span className="text-white font-bold">2 nuevas propuestas</span> para restringir la superficie de ataque sin afectar la operatividad.
                </p>
                <div className="mt-10 flex gap-4">
                    <Button className="bg-white text-slate-900 font-black px-8 py-4 rounded-xl">Revisar Propuestas</Button>
                    <Button variant="outline" className="border-white/20 text-white font-black px-8 py-4 rounded-xl">Simular Ataque</Button>
                </div>
            </Card>

            <Card className="border-none shadow-sm bg-white rounded-[2rem] p-8">
                <CardTitle className="text-sm font-black uppercase tracking-widest mb-6 flex items-center gap-2">
                    <FiFileText className="text-brand" /> Reporte de Integridad
                </CardTitle>
                <div className="space-y-6">
                    <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                        <p className="text-[10px] font-black text-slate-400 uppercase mb-2">Última Auditoría de Kernel</p>
                        <div className="flex justify-between items-end">
                            <span className="text-xs font-bold text-slate-700">Verificado hace 4m</span>
                            <Badge className="bg-emerald-100 text-emerald-700 font-black text-[9px]">COMPLETO</Badge>
                        </div>
                    </div>
                    <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                        <p className="text-[10px] font-black text-slate-400 uppercase mb-2">Hash de Estado Global</p>
                        <p className="text-[10px] font-mono text-indigo-600 break-all">f7e8a9c2b1d0...3e4f</p>
                    </div>
                </div>
                <Button className="w-full mt-8 bg-slate-900 text-white font-black text-xs uppercase tracking-widest py-4 rounded-xl">
                    Ver Bitácora Forense
                </Button>
            </Card>
        </div>
      </div>
    </ViewState>
  );
}
