'use client';

import React, { useState, useEffect } from 'react';
import { voiceEndpoints } from '@/services/endpoints/voice';
import { DataTable } from '@/ui/components/data/DataTable';
import { FiMic, FiZap, FiCheckCircle, FiXCircle, FiPlay } from 'react-icons/fi';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';

export default function VoiceAuditLogPage() {
  const [logs, setLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await voiceEndpoints.getVoiceLogs();
        setLogs(res.data.results || []);
      } catch (err) {
        console.error("Error fetching voice logs", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchLogs();
  }, []);

  const columns = [
    {
      header: 'Usuario',
      accessor: (item: any) => (
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-400">
            <FiMic size={14} />
          </div>
          <span className="font-bold">{item.user_display || item.user}</span>
        </div>
      )
    },
    {
      header: 'Comando Transcrito',
      accessor: (item: any) => (
        <p className="max-w-md truncate italic text-[var(--text-secondary)]">"{item.transcribed_text}"</p>
      )
    },
    {
      header: 'Intención',
      accessor: (item: any) => (
        <Badge className="bg-indigo-50 text-indigo-600 border-none">
          {item.detected_intent || 'PENDIENTE'}
        </Badge>
      )
    },
    {
      header: 'Estatus',
      accessor: (item: any) => (
        <div className="flex items-center gap-2">
          {item.final_status === 'COMPLETADA' ? <FiCheckCircle className="text-emerald-500" /> :
           item.final_status === 'REJECTED' ? <FiXCircle className="text-rose-500" /> :
           <FiPlay className="text-indigo-500 animate-pulse" />}
          <span className="text-[10px] font-black uppercase tracking-tighter">{item.final_status}</span>
        </div>
      )
    },
    {
      header: 'Fecha/Hora',
      accessor: (item: any) => new Date(item.timestamp_start).toLocaleString()
    },
    {
      header: 'Audio',
      accessor: (item: any) => item.audio_url ? (
        <Button variant="ghost" size="sm" onClick={() => new Audio(item.audio_url).play()}>
          <FiPlay />
        </Button>
      ) : '--',
      align: 'right' as const
    }
  ];

  return (
    <div className="p-8 space-y-10 animate-in fade-in duration-700">
      <div className="flex justify-between items-center border-b border-[var(--border-default)] pb-8">
        <div>
          <h1 className="text-4xl font-black tracking-tighter uppercase italic">Auditoría de Comandos SADI</h1>
          <p className="text-[var(--text-muted)] text-lg">Trazabilidad total de interacciones verbales y misiones de agentes.</p>
        </div>
        <Button onClick={() => window.location.reload()} variant="outline">Actualizar Log</Button>
      </div>

      <DataTable
        columns={columns}
        data={logs}
        isLoading={isLoading}
        emptyMessage="No se han registrado interacciones de voz recientemente."
      />
    </div>
  );
}
