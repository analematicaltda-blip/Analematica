'use client';

import React from 'react';
import { FiInfo, FiDatabase, FiClock, FiShield, FiDownload } from 'react-icons/fi';
import { auditLogger } from '@/services/auditLogger';
import { useAuth } from '@/contexts/AuthContext';

export interface TraceabilityInfo {
  source: string; // e.g. /api/finanzas/flujo-caja/
  model?: string; // e.g. TransaccionBancaria
  period?: string; // e.g. Enero 2026
  timestamp: string; // e.g. 2026-01-28 14:32
  status: 'OK' | 'WARN' | 'ERROR' | 'INFO' | 'DEV';
  certainty?: string; // e.g. Datos reales - Backend validado
}

interface TraceabilityBannerProps {
  info: TraceabilityInfo;
  className?: string;
}

const statusConfig = {
  OK: { color: 'bg-emerald-50 text-emerald-700 border-emerald-200', label: 'Validado', dot: 'bg-emerald-500' },
  WARN: { color: 'bg-amber-50 text-amber-700 border-amber-200', label: 'Incompleto', dot: 'bg-amber-500' },
  ERROR: { color: 'bg-red-50 text-red-700 border-red-200', label: 'Inconsistente', dot: 'bg-red-500' },
  INFO: { color: 'bg-blue-50 text-blue-700 border-blue-200', label: 'Informativo', dot: 'bg-blue-500' },
  DEV: { color: 'bg-slate-50 text-slate-700 border-slate-200', label: 'En Desarrollo', dot: 'bg-slate-500' },
};

export const TraceabilityBanner: React.FC<TraceabilityBannerProps> = ({ info, className = '' }) => {
  const config = statusConfig[info.status];
  const { user } = useAuth();

  const handleExport = () => {
    auditLogger.log({
        type: 'ACTION_PERMITTED',
        view: info.source,
        action: 'Export View Evidence',
        userRole: user?.role || 'Soberano',
        userEmail: user?.email,
        status: 'INFO'
    });
    window.print();
  };

  return (
    <div className={`flex flex-wrap items-center gap-x-6 gap-y-2 px-4 py-2 border rounded-xl text-[10px] font-bold uppercase tracking-wider ${config.color} ${className}`}>
      <div className="flex items-center gap-2">
        <FiDatabase className="opacity-50" />
        <span className="opacity-50">Fuente:</span>
        <span>{info.source}</span>
      </div>

      {info.model && (
        <div className="flex items-center gap-2">
          <FiShield className="opacity-50" />
          <span className="opacity-50">Modelo:</span>
          <span>{info.model}</span>
        </div>
      )}

      {info.period && (
        <div className="flex items-center gap-2">
          <FiClock className="opacity-50" />
          <span className="opacity-50">Periodo:</span>
          <span>{info.period}</span>
        </div>
      )}

      <div className="flex items-center gap-2">
        <FiClock className="opacity-50" />
        <span className="opacity-50">Actualización:</span>
        <span>{info.timestamp}</span>
      </div>

      <div className="flex items-center gap-2 ml-auto">
        <div className={`w-2 h-2 rounded-full ${config.dot}`}></div>
        <span>Estado: {info.certainty || config.label}</span>

        <button
          onClick={handleExport}
          className="ml-4 flex items-center gap-1 bg-white/20 hover:bg-white/40 px-2 py-1 rounded transition-colors"
          title="Generar Evidencia para Auditoría"
        >
          <FiDownload size={12} />
          EVIDENCIA
        </button>
      </div>
    </div>
  );
};
