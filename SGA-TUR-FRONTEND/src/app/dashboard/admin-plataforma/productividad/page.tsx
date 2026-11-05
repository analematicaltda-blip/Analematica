'use client';

import React from 'react';
import useSWR from 'swr';
import api from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { ViewState } from '@/components/ui/ViewState';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { FiActivity, FiUsers, FiCpu, FiZap, FiBarChart2 } from 'react-icons/fi';

const fetcher = (url: string) => api.get(url).then(res => res.data);

export default function ProductivityPage() {
    const { data, isLoading, error } = useSWR('/sarita/metrics/productivity/', fetcher, {
        refreshInterval: 30000 // Refrescar cada 30 segundos
    });

    return (
        <div className="p-8 space-y-10 animate-in fade-in duration-700">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-4xl font-black text-slate-900 tracking-tighter uppercase italic">Métricas de Productividad SARITA</h1>
                    <p className="text-slate-500 text-lg">Panel interno de rendimiento jerárquico (Fase 4.2).</p>
                </div>
                <div className="bg-slate-100 p-4 rounded-2xl flex items-center gap-3">
                    <div className="w-2 h-2 bg-emerald-500 rounded-full animate-ping" />
                    <span className="text-xs font-black uppercase tracking-widest text-slate-600">Sincronización en Tiempo Real</span>
                </div>
            </div>

            <ViewState isLoading={isLoading} error={error} isSilentLoading={!!data}>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <Card className="border-none shadow-sm bg-white">
                        <CardContent className="p-8 flex items-center justify-between">
                            <div>
                                <p className="text-[10px] font-black text-slate-400 uppercase mb-1">Misiones Capitanes</p>
                                <h3 className="text-3xl font-black">{data?.levels?.capitanes?.length || 0}</h3>
                            </div>
                            <div className="p-4 bg-indigo-50 text-indigo-600 rounded-2xl">
                                <FiCpu size={24} />
                            </div>
                        </CardContent>
                    </Card>
                    {/* ... más KPIs ... */}
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Tabla de Soldados */}
                    <Card className="border-none shadow-sm overflow-hidden bg-white">
                        <CardHeader className="bg-slate-50 p-6 border-b">
                            <CardTitle className="text-sm font-black uppercase tracking-widest flex items-center gap-2">
                                <FiUsers className="text-brand" /> Rendimiento de Soldados (Nivel 6)
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="p-0">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead className="px-6">Identificador</TableHead>
                                        <TableHead className="text-center">Total</TableHead>
                                        <TableHead className="text-center">Éxito</TableHead>
                                        <TableHead className="text-right px-6">Ratio</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {data?.levels?.soldados?.map((s: any, i: number) => (
                                        <TableRow key={i}>
                                            <TableCell className="px-6 font-bold">{s.soldado_asignado}</TableCell>
                                            <TableCell className="text-center">{s.total}</TableCell>
                                            <TableCell className="text-center text-emerald-600 font-bold">{s.exitosas}</TableCell>
                                            <TableCell className="text-right px-6">
                                                <Badge className="bg-slate-100 text-slate-700">
                                                    {((s.exitosas / s.total) * 100).toFixed(1)}%
                                                </Badge>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </CardContent>
                    </Card>

                    {/* Tabla de Tenientes */}
                    <Card className="border-none shadow-sm overflow-hidden bg-white">
                        <CardHeader className="bg-slate-50 p-6 border-b">
                            <CardTitle className="text-sm font-black uppercase tracking-widest flex items-center gap-2">
                                <FiZap className="text-amber-500" /> Eficiencia de Tenientes (Nivel 4)
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="p-0">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead className="px-6">Teniente</TableHead>
                                        <TableHead className="text-center">Misiones</TableHead>
                                        <TableHead className="text-right px-6">Tiempo Avg</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {data?.levels?.tenientes?.map((t: any, i: number) => (
                                        <TableRow key={i}>
                                            <TableCell className="px-6 font-bold">{t.teniente_asignado}</TableCell>
                                            <TableCell className="text-center">{t.total}</TableCell>
                                            <TableCell className="text-right px-6 font-mono text-xs">
                                                {t.tiempo_promedio || 'N/A'}
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </CardContent>
                    </Card>
                </div>
            </ViewState>
        </div>
    );
}
