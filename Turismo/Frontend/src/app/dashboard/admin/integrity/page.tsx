'use client';

import React, { useState, useEffect } from 'react';
import { FiShield, FiAlertTriangle, FiCheckCircle, FiActivity, FiLayers, FiDatabase, FiRefreshCw } from 'react-icons/fi';
import { toast } from 'react-toastify';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface AuditComponent {
  component: string;
  status: string;
  score: number;
  message?: string;
  violations: any[];
  metrics?: any;
}

interface IntegrityReport {
  certification_id: string;
  timestamp: string;
  overall_status: string;
  certification_level: string;
  integrity_score: number;
  components: AuditComponent[];
  verdict: string;
}

export default function IntegrityDashboard() {
  const [report, setReport] = useState<IntegrityReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/governance/integrity/status/`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (res.ok) {
        const data = await res.json();
        setReport(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const runCertification = async () => {
    setRunning(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/governance/integrity/run/`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (res.ok) {
        const data = await res.json();
        setReport(data);
        toast.success(`Certificación completada: Nivel ${data.certification_level}`);
      }
    } catch (err) {
      toast.error("Error al ejecutar la certificación.");
    } finally {
      setRunning(false);
    }
  };

  useEffect(() => { fetchStatus(); }, []);

  if (loading) return <div className="p-12 text-center animate-pulse text-slate-500">Analizando integridad sistémica...</div>;

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'A': return 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20';
      case 'B': return 'text-blue-500 bg-blue-500/10 border-blue-500/20';
      case 'C': return 'text-amber-500 bg-amber-500/10 border-amber-500/20';
      default: return 'text-red-500 bg-red-500/10 border-red-500/20';
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-black tracking-tighter text-slate-900 uppercase flex items-center gap-4">
            <FiShield className="text-brand" />
            Certificación de Integridad
          </h1>
          <p className="text-slate-500 mt-2 font-medium">Auditoría automática de arquitectura, persistencia y ledger (Fase 7)</p>
        </div>
        <button
          onClick={runCertification}
          disabled={running}
          className="bg-slate-900 text-white px-6 py-3 rounded-2xl font-black uppercase tracking-widest text-xs flex items-center gap-3 hover:bg-brand transition-all disabled:opacity-50"
        >
          {running ? <FiRefreshCw className="animate-spin" /> : <FiActivity />}
          {running ? 'Certificando...' : 'Ejecutar Auditoría Total'}
        </button>
      </header>

      {!report ? (
        <div className="bg-slate-50 border-2 border-dashed border-slate-200 rounded-[2.5rem] p-20 text-center">
          <FiAlertTriangle className="mx-auto text-slate-300 mb-6" size={64} />
          <h2 className="text-2xl font-bold text-slate-400">Sin Certificación Activa</h2>
          <p className="text-slate-400 mt-2">El sistema no ha sido auditado en este ciclo.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Score Card */}
          <div className={`lg:col-span-1 rounded-[2.5rem] p-10 border-2 flex flex-col items-center justify-center text-center ${getLevelColor(report.certification_level)}`}>
            <span className="text-[10px] font-black uppercase tracking-[0.3em] mb-4">Nivel Alcanzado</span>
            <div className="text-9xl font-black mb-6">{report.certification_level}</div>
            <div className="text-2xl font-bold uppercase tracking-tight mb-2">{report.verdict}</div>
            <div className="text-sm font-medium opacity-70">Score Global: {report.integrity_score}%</div>
            <div className="mt-8 pt-8 border-t border-current/10 w-full text-[10px] font-mono opacity-50">
              ID: {report.certification_id}<br/>
              {new Date(report.timestamp).toLocaleString()}
            </div>
          </div>

          {/* Component Details */}
          <div className="lg:col-span-2 space-y-6">
            <h3 className="text-xs font-black uppercase tracking-widest text-slate-400 ml-4">Resultados por Componente</h3>
            {report.components.map((c, i) => (
              <div key={i} className="bg-white border border-slate-100 rounded-3xl p-6 shadow-sm hover:shadow-md transition-all">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${c.status === 'PASSED' ? 'bg-emerald-50 text-emerald-500' : 'bg-red-50 text-red-500'}`}>
                      {c.component === 'DomainIsolation' ? <FiLayers size={24}/> :
                       c.component === 'AccountingIntegrity' ? <FiDatabase size={24}/> :
                       <FiCheckCircle size={24}/>}
                    </div>
                    <div>
                      <h4 className="font-bold text-lg text-slate-800">{c.component}</h4>
                      <p className="text-xs text-slate-500 uppercase font-black tracking-widest">{c.status}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-black text-slate-900">{c.score}%</div>
                    <div className="w-24 h-1.5 bg-slate-100 rounded-full mt-2 overflow-hidden">
                      <div className="h-full bg-brand" style={{width: `${c.score}%`}} />
                    </div>
                  </div>
                </div>

                {c.violations.length > 0 && (
                  <div className="mt-4 p-4 bg-red-50 rounded-2xl border border-red-100">
                    <p className="text-xs font-bold text-red-600 uppercase mb-2 flex items-center gap-2">
                      <FiAlertTriangle /> Violaciones Detectadas ({c.violations.length})
                    </p>
                    <ul className="space-y-2">
                      {c.violations.slice(0, 3).map((v, j) => (
                        <li key={j} className="text-xs text-red-800 flex gap-2">
                          <span className="opacity-50">•</span>
                          {v.message || v.type}
                        </li>
                      ))}
                      {c.violations.length > 3 && <li className="text-[10px] text-red-400 italic">... y {c.violations.length - 3} más.</li>}
                    </ul>
                  </div>
                )}

                {c.metrics && (
                   <div className="mt-4 flex gap-4">
                      {Object.entries(c.metrics).map(([k, v]: [string, any], j) => (
                        <div key={j} className="bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-100">
                          <span className="text-[9px] font-black text-slate-400 uppercase mr-2">{k}:</span>
                          <span className="text-[10px] font-bold text-slate-700">{typeof v === 'string' ? v.substring(0, 12) : v}</span>
                        </div>
                      ))}
                   </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
