'use client';

import React, { useState, useEffect } from 'react';
import { FiShield, FiAnchor, FiActivity, FiMap, FiCheckCircle, FiClock } from 'react-icons/fi';
import { httpClient } from '@/services/httpClient';

export default function LegacyDashboardPage() {
  const [legacyData, setLegacyData] = useState<Record<string, any> | null>(null);

  useEffect(() => {
    httpClient.get('/v1/legacy/dashboard/')
      .then(res => setLegacyData(res.data))
      .catch(err => console.error(err));
  }, []);

  const principles = [
    { title: 'Subordinación Soberana', desc: 'Delegación algorítmica condicionada al mandato humano.' },
    { title: 'Imprivatizabilidad', desc: 'SARITA es un bien público civilizatorio inalienable.' },
    { title: 'Anti-Deriva Histórica', desc: 'Prohibición de expansión de mandato o auto-modificación.' },
    { title: 'Transmisión de Sabiduría', desc: 'Custodia del porqué técnico y ético del sistema.' },
  ];

  return (
    <div className="p-8 bg-black min-h-screen text-teal-500 font-mono">
      <div className="border-2 border-teal-900 p-6 rounded-lg bg-gray-900/50 backdrop-blur-md">
        <div className="flex items-center gap-4 mb-8 border-b border-teal-900 pb-4">
          <FiShield className="text-4xl text-teal-400 animate-pulse" />
          <div>
            <h1 className="text-3xl font-bold uppercase tracking-tighter text-teal-100">Custodia de Legado SARITA</h1>
            <p className="text-teal-600">Estado: <span className="text-green-400 underline italic">LEGADO_PROTEGIDO</span> | Ref: RC-S-CONSOLIDATED</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {principles.map((p, i) => (
            <div key={i} className="border border-teal-900/50 p-4 rounded bg-black/40 hover:border-teal-500 transition-colors group">
              <div className="flex items-center gap-3 mb-2">
                <FiAnchor className="text-teal-400 group-hover:rotate-45 transition-transform" />
                <h3 className="text-teal-100 font-bold">{p.title}</h3>
              </div>
              <p className="text-sm text-teal-700 italic leading-snug">{p.desc}</p>
            </div>
          ))}
        </div>

        <div className="bg-teal-900/10 border border-teal-900 p-4 rounded-lg mb-8">
          <h2 className="text-lg font-bold text-teal-300 mb-4 flex items-center gap-2">
            <FiActivity className="text-teal-400" /> BITÁCORA DE TRANSMISIÓN GENERACIONAL
          </h2>
          <div className="space-y-3">
            {legacyData?.recent_milestones?.length > 0 ? (
              legacyData.recent_milestones.map((m: Record<string, any>, i: number) => (
                <div key={i} className="flex justify-between text-xs border-l-2 border-teal-800 pl-4 py-1">
                  <div>
                    <span className="text-teal-400 font-bold">{m.title}</span>
                    <p className="text-[10px] text-teal-700 font-mono mt-1">HASH: {m.integrity_hash.substring(0, 16)}...</p>
                  </div>
                  <span className="text-teal-600">{new Date(m.timestamp).toLocaleDateString()}</span>
                  <span className="text-green-900 font-bold px-2 bg-green-400/10 rounded self-start">SELLADO</span>
                </div>
              ))
            ) : (
              <div className="text-teal-800 text-xs italic p-4 text-center border border-dashed border-teal-900 rounded">
                Sin hitos históricos registrados en la cadena de custodia actual.
              </div>
            )}
          </div>
        </div>

        {legacyData?.active_guardrails?.length > 0 && (
          <div className="mb-8 grid grid-cols-1 md:grid-cols-2 gap-4">
             <div className="border border-teal-900 p-4 rounded bg-teal-950/20">
                <h3 className="text-xs font-black text-teal-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                   <FiCheckCircle /> Guardrails Activos
                </h3>
                <div className="space-y-2">
                   {legacyData.active_guardrails.map((g: Record<string, any>, i: number) => (
                      <div key={i} className="text-[10px] flex items-center gap-2">
                         <div className="w-1 h-1 bg-green-500 rounded-full" />
                         <span className="text-teal-300 font-bold">{g.name}</span>
                      </div>
                   ))}
                </div>
             </div>
             <div className="border border-teal-900 p-4 rounded bg-teal-950/20">
                <h3 className="text-xs font-black text-teal-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                   <FiClock /> Métricas de Legado
                </h3>
                <div className="grid grid-cols-2 gap-2 text-[10px]">
                   <div className="text-teal-700">Custodios: <span className="text-teal-300">{legacyData.active_custodians}</span></div>
                   <div className="text-teal-700">Integridad: <span className="text-teal-300">SHA-256</span></div>
                   <div className="text-teal-700">Estado: <span className="text-teal-300">{legacyData.status}</span></div>
                </div>
             </div>
          </div>
        )}

        <div className="border border-red-900/50 bg-red-950/10 p-4 rounded text-center">
          <p className="text-red-500 text-xs uppercase font-bold tracking-widest">
             Aviso de Seguridad Institucional: Cualquier intento de desvío del modelo original activará de-interoperabilidad inmediata.
          </p>
        </div>
      </div>
    </div>
  );
}
