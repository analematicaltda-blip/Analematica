'use client';

import React from 'react';
import { useIntelligenceApi } from './hooks/useIntelligenceApi';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { Brain, Play, CheckCircle, AlertTriangle } from 'lucide-react';
import { toast } from 'react-hot-toast';

export default function InteligenciaDecisoraPage() {
  const { proposals, isLoading, runAnalysis, approveProposal, executeProposal } = useIntelligenceApi();

  const handleRunAnalysis = async () => {
    toast.promise(runAnalysis(), {
      loading: 'IA analizando el sistema...',
      success: 'Análisis completado.',
      error: 'Error al ejecutar análisis.'
    });
  };

  const handleApprove = async (id: string) => {
    await approveProposal(id);
    toast.success('Propuesta aprobada.');
  };

  const handleExecute = async (id: string) => {
    try {
      const res = await executeProposal(id);
      toast.success('Ejecución soberana completada con éxito.');
    } catch (err: any) {
      toast.error(`Error: ${err.response?.data?.error || 'No se pudo ejecutar'}`);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Inteligencia de Decisión Soberana</h1>
        <Button onClick={handleRunAnalysis} className="bg-purple-600 hover:bg-purple-700">
          <Brain className="mr-2 h-4 w-4" />
          Ejecutar Auditoría IA
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recomendaciones Estratégicas Pendientes</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <p>Cargando propuestas...</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Dominio</TableHead>
                    <TableHead>Contexto / Oportunidad</TableHead>
                    <TableHead>Riesgo</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead>Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {proposals.map((p: any) => (
                    <TableRow key={p.id}>
                      <TableCell className="font-bold">{p.domain_display}</TableCell>
                      <TableCell>
                        <div className="text-sm">
                          <p className="font-semibold text-blue-700">{p.contexto_detectado}</p>
                          <p className="text-gray-600 mt-1 italic">"{p.oportunidad_detectada}"</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={p.nivel_riesgo === 'HIGH' ? 'destructive' : 'default'}>
                          {p.risk_display}
                        </Badge>
                      </TableCell>
                      <TableCell>
                         <Badge variant="outline">{p.status_display}</Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          {p.status === 'PENDING' && (
                            <Button size="sm" onClick={() => handleApprove(p.id)}>
                              <CheckCircle className="h-4 w-4 mr-1" /> Aprobar
                            </Button>
                          )}
                          {p.status === 'APPROVED' && (
                            <Button size="sm" variant="outline" onClick={() => handleExecute(p.id)} className="border-green-600 text-green-600 hover:bg-green-50">
                              <Play className="h-4 w-4 mr-1" /> Ejecutar
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                  {proposals.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-8 text-gray-500">
                        No hay propuestas pendientes. Ejecute una auditoría para detectar oportunidades.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
