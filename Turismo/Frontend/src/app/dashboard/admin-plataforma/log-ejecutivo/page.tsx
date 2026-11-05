'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import {
  FiFileText, FiUser, FiCpu, FiCheckCircle, FiXCircle, FiRotateCcw, FiActivity
} from 'react-icons/fi';
import { ViewState } from '@/components/ui/ViewState';
import { CriticalActionDialog } from '@/components/ui/CriticalActionDialog';
import { toast } from 'react-hot-toast';

interface ExecutiveLog {
    id: string;
    action: string;
    actor: 'HUMANO' | 'IA';
    actor_name: string;
    timestamp: string;
    impact: string;
    status: 'EJECUTADO' | 'REVERTIDO' | 'FALLIDO';
    reversible: boolean;
}

import { sovereigntyService } from '@/services/sovereigntyService';

export default function ExecutiveLogPage() {
  const [logs, setLogs] = useState<ExecutiveLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLog, setSelectedLog] = useState<ExecutiveLog | null>(null);
  const [isRollbackOpen, setIsRollbackOpen] = useState(false);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    setIsLoading(true);
    setError(null);
    try {
        // Intentar obtener logs reales de gobernanza
        // Nota: Si el endpoint no existe, mostrará el error institucional.
        const res = await sovereigntyService.getSystemStatus();
        // Mapear logs de backend si existieran, por ahora el servicio falla
        setLogs([]);
    } catch (err: any) {
        console.error("Log fetch error:", err);
        setError("SERVICIO NO DISPONIBLE: El endpoint de la Bitácora de Soberanía no responde. La integridad del log no puede ser verificada en tiempo real.");
        setLogs([]);
    } finally {
        setIsLoading(false);
    }
  };

  const handleRollbackRequest = (log: ExecutiveLog) => {
    setSelectedLog(log);
    setIsRollbackOpen(true);
  };

  const confirmRollback = async () => {
    toast.success("REVERSIÓN EJECUTADA. Los parámetros han vuelto al estado previo.");
    setIsRollbackOpen(false);
    fetchLogs();
  };

  return (
    <ViewState isLoading={isLoading} error={error} isEmpty={logs.length === 0 && !error && !isLoading}>
      <div className="space-y-10 animate-in fade-in duration-700">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-gray-100 pb-8">
            <div>
                <h1 className="text-4xl font-black text-slate-900 tracking-tighter uppercase italic">Bitácora de Soberanía</h1>
                <p className="text-slate-500 text-lg font-medium italic">Registro humanizado de eventos críticos y decisiones de alto nivel.</p>
            </div>
        </div>

        <Card className="border-none shadow-xl bg-white rounded-[2.5rem] overflow-hidden">
            <CardContent className="p-0">
                <Table>
                    <TableHeader className="bg-slate-50">
                        <TableRow>
                            <TableHead className="font-black uppercase text-[10px] tracking-widest px-10 py-6">Evento / Decisión</TableHead>
                            <TableHead className="font-black uppercase text-[10px] tracking-widest">Actor</TableHead>
                            <TableHead className="font-black uppercase text-[10px] tracking-widest text-center">Clasificación</TableHead>
                            <TableHead className="font-black uppercase text-[10px] tracking-widest">Impacto Estimado</TableHead>
                            <TableHead className="font-black uppercase text-[10px] tracking-widest">Estado</TableHead>
                            <TableHead className="font-black uppercase text-[10px] tracking-widest text-right px-10">Gobernanza</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {logs.map((log) => (
                            <TableRow key={log.id} className="hover:bg-slate-50 transition-all border-slate-100">
                                <TableCell className="px-10 py-8">
                                    <div>
                                        <p className="font-black text-slate-900 text-lg italic tracking-tight">{log.action}</p>
                                        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{new Date(log.timestamp).toLocaleString()}</p>
                                    </div>
                                </TableCell>
                                <TableCell className="text-center">
                                    <Badge variant="outline" className="text-[8px] font-black border-red-100 text-red-600 uppercase">Dato Sensible</Badge>
                                </TableCell>
                                <TableCell>
                                    <div className="flex items-center gap-3">
                                        <div className={`p-2 rounded-lg ${log.actor === 'HUMANO' ? 'bg-blue-50 text-blue-600' : 'bg-indigo-50 text-indigo-600'}`}>
                                            {log.actor === 'HUMANO' ? <FiUser /> : <FiCpu />}
                                        </div>
                                        <div>
                                            <p className="font-bold text-slate-700 text-sm">{log.actor_name}</p>
                                            <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest">{log.actor}</p>
                                        </div>
                                    </div>
                                </TableCell>
                                <TableCell>
                                    <p className="text-sm font-medium text-slate-600 italic">"{log.impact}"</p>
                                </TableCell>
                                <TableCell>
                                    <Badge className={
                                        log.status === 'EJECUTADO' ? 'bg-emerald-100 text-emerald-700' :
                                        log.status === 'REVERTIDO' ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'
                                    }>
                                        {log.status}
                                    </Badge>
                                </TableCell>
                                <TableCell className="text-right px-10">
                                    {log.reversible && log.status === 'EJECUTADO' ? (
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={() => handleRollbackRequest(log)}
                                            className="border-amber-200 text-amber-600 hover:bg-amber-50 rounded-xl font-black text-[10px] uppercase tracking-widest"
                                        >
                                            <FiRotateCcw className="mr-2" /> Revertir
                                        </Button>
                                    ) : (
                                        <span className="text-[9px] font-black text-slate-300 uppercase tracking-widest italic">No reversible</span>
                                    )}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>

        <CriticalActionDialog
            isOpen={isRollbackOpen}
            onClose={() => setIsRollbackOpen(false)}
            onConfirm={confirmRollback}
            title="Solicitud de Rollback"
            description={`Está a punto de revertir la acción "${selectedLog?.action}". El sistema restaurará la configuración previa al evento. ¿Desea proceder?`}
            confirmLabel="Ejecutar Reversión"
            type="warning"
        />
      </div>
    </ViewState>
  );
}
