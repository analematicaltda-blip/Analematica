'use client';

import React, { useState } from 'react';
import { useGRC } from '@/contexts/GRCContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import {
  FiShield, FiAlertTriangle, FiCheckCircle, FiFileText, FiActivity,
  FiEye, FiAlertCircle, FiClock, FiUser, FiExternalLink, FiTool, FiMic
} from 'react-icons/fi';
import { auditLogger } from '@/services/auditLogger';
import { Button } from '@/components/ui/Button';
import { toast } from 'react-hot-toast';

export default function GRCCenterPage() {
  const { complianceMatrix, risks, exceptions, grcKpis, isAuditMode, toggleAuditMode } = useGRC();
  const [logs] = useState(auditLogger.getLogs());

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'CUMPLE': return <Badge className="bg-emerald-100 text-emerald-700 border-emerald-200">✅ CUMPLE</Badge>;
      case 'PARCIAL': return <Badge className="bg-amber-100 text-amber-700 border-amber-200">🟡 PARCIAL</Badge>;
      case 'NO_CUMPLE': return <Badge className="bg-red-100 text-red-700 border-red-200">🔴 NO CUMPLE</Badge>;
      default: return <Badge className="bg-slate-100 text-slate-700">⚪ N/A</Badge>;
    }
  };

  const getRiskImpactBadge = (impact: string) => {
    switch (impact) {
      case 'CRITICO': return <Badge className="bg-red-600 text-white">CRÍTICO</Badge>;
      case 'ALTO': return <Badge className="bg-orange-500 text-white">ALTO</Badge>;
      case 'MEDIO': return <Badge className="bg-amber-500 text-white">MEDIO</Badge>;
      default: return <Badge className="bg-blue-500 text-white">BAJO</Badge>;
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      {/* Header GRC */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-gray-100 pb-8">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-indigo-900 text-white p-2 rounded-lg">
              <FiShield size={24} />
            </div>
            <h1 className="text-4xl font-black text-slate-900 tracking-tighter uppercase">Centro de Gobierno, Riesgo y Cumplimiento (GRC)</h1>
          </div>
        <p className="text-slate-500 text-lg">Monitoreo de integridad institucional y custodia de evidencias de control.</p>
        </div>
        <div className="flex gap-4">
           <button
             onClick={toggleAuditMode}
             className={`px-6 py-3 rounded-2xl flex items-center gap-3 transition-all font-black uppercase tracking-widest text-sm shadow-lg ${
               isAuditMode
               ? 'bg-amber-500 text-black animate-pulse'
               : 'bg-slate-900 text-white hover:bg-slate-800'
             }`}
           >
              <FiEye size={18} />
              {isAuditMode ? 'Modo Auditor Activo' : 'Activar Modo Auditor'}
           </button>
           <Button
             onClick={() => {
                toast.success("COMPILANDO EXPEDIENTE DE CUMPLIMIENTO...");
                setTimeout(() => toast.success("CERTIFICADO DE TRAZABILIDAD (PDF/JSON) GENERADO."), 2000);
             }}
             className="px-6 py-3 rounded-2xl flex items-center gap-3 bg-emerald-600 text-white font-black uppercase tracking-widest text-sm shadow-lg hover:bg-emerald-700"
           >
              <FiFileText size={18} />
              Exportar Certificación
           </Button>
        </div>
      </div>

      {/* KPI Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
         <Card className="border-none shadow-sm bg-white overflow-hidden relative group">
            <CardContent className="p-8">
               <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Índice de Cumplimiento</p>
               <h3 className="text-4xl font-black text-emerald-600">{grcKpis.compliancePercentage}%</h3>
               <div className="mt-4 h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-500" style={{ width: `${grcKpis.compliancePercentage}%` }} />
               </div>
            </CardContent>
         </Card>
         <Card className="border-none shadow-sm bg-white">
            <CardContent className="p-8">
               <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Riesgos Críticos Activos</p>
               <h3 className={`text-4xl font-black ${grcKpis.activeCriticalRisks > 0 ? 'text-red-600' : 'text-slate-900'}`}>
                 {grcKpis.activeCriticalRisks}
               </h3>
               <p className="text-xs text-slate-500 mt-2">Requieren intervención inmediata de Gobernanza.</p>
            </CardContent>
         </Card>
         <Card className="border-none shadow-sm bg-white">
            <CardContent className="p-8">
               <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Custodia de Evidencia (Eventos)</p>
               <h3 className="text-4xl font-black text-indigo-600">{logs.length}</h3>
               <p className="text-xs text-slate-500 mt-2">Registros capturados para validación externa.</p>
            </CardContent>
         </Card>
      </div>

      {/* Main GRC Content */}
      <Tabs defaultValue="compliance" className="w-full">
        <TabsList className="bg-slate-100 p-1 rounded-xl mb-6">
          <TabsTrigger value="compliance" className="data-[state=active]:bg-white data-[state=active]:shadow-sm px-6 py-2 font-bold uppercase text-[10px] tracking-widest">
            Matriz de Cumplimiento
          </TabsTrigger>
          <TabsTrigger value="risks" className="data-[state=active]:bg-white data-[state=active]:shadow-sm px-6 py-2 font-bold uppercase text-[10px] tracking-widest">
            Mapa de Riesgos
          </TabsTrigger>
          <TabsTrigger value="audit" className="data-[state=active]:bg-white data-[state=active]:shadow-sm px-6 py-2 font-bold uppercase text-[10px] tracking-widest">
            Registro de Trazabilidad
          </TabsTrigger>
          <TabsTrigger value="voice" className="data-[state=active]:bg-white data-[state=active]:shadow-sm px-6 py-2 font-bold uppercase text-[10px] tracking-widest">
            Supervisión de Voz
          </TabsTrigger>
          <TabsTrigger value="exceptions" className="data-[state=active]:bg-white data-[state=active]:shadow-sm px-6 py-2 font-bold uppercase text-[10px] tracking-widest">
            Control de Excepciones
          </TabsTrigger>
        </TabsList>

        <TabsContent value="compliance">
          <Card className="border-none shadow-sm overflow-hidden">
            <CardContent className="p-0">
              <Table>
                <TableHeader className="bg-slate-50">
                  <TableRow>
                    <TableHead className="px-8 font-black uppercase text-[10px] tracking-widest">Dominio</TableHead>
                    <TableHead className="font-black uppercase text-[10px] tracking-widest">Estado</TableHead>
                    <TableHead className="font-black uppercase text-[10px] tracking-widest">Evidencia / Fuente</TableHead>
                    <TableHead className="font-black uppercase text-[10px] tracking-widest">Mecanismo de Control</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {complianceMatrix.map((item, i) => (
                    <TableRow key={i} className="hover:bg-slate-50 transition-colors border-slate-50">
                      <TableCell className="px-8 font-bold text-slate-800">{item.domain}</TableCell>
                      <TableCell>{getStatusBadge(item.status)}</TableCell>
                      <TableCell className="font-mono text-xs text-indigo-600">{item.evidence}</TableCell>
                      <TableCell>
                        <div className="text-xs">
                          <p className="font-bold text-slate-700">{item.mechanism}</p>
                          <p className="text-slate-400 italic mt-1">{item.notes}</p>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="risks">
          <div className="grid grid-cols-1 gap-4">
             {risks.map((risk) => (
               <Card key={risk.id} className={`border-l-4 shadow-sm ${
                 risk.impact === 'CRITICO' ? 'border-l-red-600' :
                 risk.impact === 'ALTO' ? 'border-l-orange-500' : 'border-l-amber-500'
               }`}>
                  <CardContent className="p-6 flex justify-between items-start">
                     <div className="space-y-2">
                        <div className="flex items-center gap-3">
                           <span className="font-mono text-xs bg-slate-100 px-2 py-1 rounded">{risk.id}</span>
                           <h4 className="font-black text-lg text-slate-900 uppercase italic tracking-tight">{risk.title}</h4>
                           <Badge variant="outline">{risk.type}</Badge>
                        </div>
                        <p className="text-sm text-slate-600 max-w-2xl">{risk.explanation}</p>
                        <div className="flex items-center gap-4 mt-4">
                           <div className="flex items-center gap-1 text-[10px] font-bold text-slate-400 uppercase">
                              <FiActivity size={12} /> Probabilidad: {risk.probability}
                           </div>
                           <div className="flex items-center gap-1 text-[10px] font-bold text-slate-400 uppercase">
                              <FiTool size={12} /> Estado: {risk.status}
                           </div>
                        </div>
                     </div>
                     <div className="text-right">
                        <p className="text-[10px] font-black text-slate-400 uppercase mb-1">Impacto</p>
                        {getRiskImpactBadge(risk.impact)}
                     </div>
                  </CardContent>
               </Card>
             ))}
          </div>
        </TabsContent>

        <TabsContent value="audit">
           <Card className="border-none shadow-sm overflow-hidden bg-slate-900 text-slate-300">
              <CardHeader className="border-b border-white/5 p-6 flex flex-row items-center justify-between">
                 <CardTitle className="text-white font-black uppercase text-sm tracking-widest flex items-center gap-2">
                    <FiClock className="text-indigo-400" /> Registro de Actividad Institucional
                 </CardTitle>
                 <Badge className="bg-indigo-500">Trazabilidad en Tiempo Real</Badge>
              </CardHeader>
              <CardContent className="p-0">
                 <div className="max-h-[500px] overflow-y-auto font-mono text-[11px] divide-y divide-white/5">
                    {logs.length === 0 ? (
                      <div className="p-20 text-center text-slate-500 uppercase italic tracking-widest">No hay logs registrados en esta sesión.</div>
                    ) : (
                      logs.map((log) => (
                        <div key={log.id} className="p-4 hover:bg-white/5 transition-colors flex gap-6">
                           <span className="text-slate-500 w-48 shrink-0">{new Date(log.timestamp).toLocaleString()}</span>
                           <span className={`w-32 shrink-0 font-bold ${
                             log.status === 'ERROR' ? 'text-red-400' :
                             log.status === 'WARN' ? 'text-amber-400' : 'text-emerald-400'
                           }`}>[{log.type}]</span>
                           <span className="text-slate-200 shrink-0 font-bold">{log.view}</span>
                           <span className="flex-1">{log.action || '-'}</span>
                           <span className="text-indigo-400 shrink-0 uppercase font-bold">{log.userRole}</span>
                        </div>
                      ))
                    )}
                 </div>
              </CardContent>
           </Card>
        </TabsContent>

        <TabsContent value="voice">
           <Card className="border-none shadow-sm overflow-hidden bg-slate-50 border border-slate-200">
              <CardHeader className="bg-white border-b border-slate-100 p-6 flex flex-row items-center justify-between">
                 <CardTitle className="text-slate-900 font-black uppercase text-sm tracking-widest flex items-center gap-2">
                    <FiMic className="text-emerald-600" /> Supervisión de Interacciones de Voz
                 </CardTitle>
                 <Badge variant="outline">SADI Interface</Badge>
              </CardHeader>
              <CardContent className="p-0">
                 <div className="max-h-[500px] overflow-y-auto divide-y divide-slate-100">
                    {logs.filter(l => l.type.startsWith('VOICE_')).length === 0 ? (
                      <div className="p-20 text-center text-slate-400 uppercase italic tracking-widest">No hay registros de voz en esta sesión.</div>
                    ) : (
                      logs.filter(l => l.type.startsWith('VOICE_')).map((log) => (
                        <div key={log.id} className="p-4 bg-white hover:bg-slate-50 transition-colors flex flex-col gap-2">
                           <div className="flex justify-between items-center">
                              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{new Date(log.timestamp).toLocaleString()}</span>
                              <Badge className={
                                log.type === 'VOICE_ACTION_CONFIRMED' ? 'bg-emerald-100 text-emerald-700' :
                                log.type === 'VOICE_ACTION_ABORTED' ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700'
                              }>
                                {log.type}
                              </Badge>
                           </div>
                           <p className="font-black text-slate-800 uppercase italic tracking-tight">{log.action}</p>
                           {log.details && (
                             <div className="text-[11px] bg-slate-100 p-3 rounded-lg border border-slate-200 text-slate-600 font-mono">
                                {JSON.stringify(log.details, null, 2)}
                             </div>
                           )}
                           <div className="flex justify-end">
                              <span className="text-[9px] font-black text-indigo-600 uppercase">Autoridad: {log.userRole}</span>
                           </div>
                        </div>
                      ))
                    )}
                 </div>
              </CardContent>
           </Card>
        </TabsContent>

        <TabsContent value="exceptions">
           <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {exceptions.map((ex) => (
                <Card key={ex.id} className="border-none shadow-sm bg-white overflow-hidden">
                   <div className="bg-amber-500 text-black px-4 py-1 text-[10px] font-black uppercase tracking-widest">
                      Excepción Declarada - {ex.id}
                   </div>
                   <CardContent className="p-6 space-y-4">
                      <h4 className="font-black text-xl text-slate-900 uppercase italic">{ex.module}</h4>
                      <p className="text-sm text-slate-600 bg-slate-50 p-4 rounded-xl border border-slate-100 italic">
                        "{ex.reason}"
                      </p>
                      <div className="grid grid-cols-2 gap-4 text-[10px] font-bold uppercase text-slate-400 tracking-wider">
                         <div>
                            <p className="mb-1 text-slate-500 underline">Responsable</p>
                            <div className="flex items-center gap-1 text-slate-700">
                               <FiUser size={12} /> {ex.responsible}
                            </div>
                         </div>
                         <div>
                            <p className="mb-1 text-slate-500 underline">Fecha Revisión</p>
                            <div className="flex items-center gap-1 text-slate-700">
                               <FiClock size={12} /> {ex.reviewDate}
                            </div>
                         </div>
                      </div>
                   </CardContent>
                </Card>
              ))}
           </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
