'use client';

import React from 'react';
import { useDashboard } from '@/contexts/DashboardContext';
import { usePermissions } from '@/ui/guards/PermissionGuard';
import { FiShield, FiAlertTriangle, FiInfo, FiLock } from 'react-icons/fi';
import { Badge } from './Badge';

interface GRCIndicatorProps {
  moduleName: string;
  risks?: string[];
  controls?: string[];
}

export const GRCIndicator: React.FC<GRCIndicatorProps> = ({ moduleName, risks = [], controls = [] }) => {
  const { isAuditMode } = useDashboard();
  const { role } = usePermissions();

  return (
    <div className={`mb-6 p-4 rounded-2xl border flex items-center justify-between transition-all ${
      isAuditMode
      ? 'bg-amber-50 border-amber-200'
      : 'bg-indigo-50/30 border-indigo-100'
    }`}>
      <div className="flex items-center gap-4">
        <div className={`p-3 rounded-xl ${isAuditMode ? 'bg-amber-500 text-black' : 'bg-indigo-600 text-white'}`}>
          {isAuditMode ? <FiShield size={20} /> : <FiLock size={20} />}
        </div>
        <div>
          <h4 className="text-xs font-black uppercase tracking-[0.2em] text-slate-400 mb-0.5">Control de Integridad GRC</h4>
          <div className="flex items-center gap-2">
            <span className="font-black text-slate-800 uppercase italic tracking-tight">{moduleName}</span>
            <Badge variant="outline" className="text-[9px] font-black border-slate-200">ROL: {role}</Badge>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-6">
        {risks.length > 0 && (
          <div className="flex items-center gap-2 group cursor-help">
            <FiAlertTriangle size={14} className="text-orange-500" />
            <span className="text-[10px] font-black text-orange-600 uppercase tracking-widest">{risks.length} Riesgos Activos</span>
          </div>
        )}
        {controls.length > 0 && (
          <div className="flex items-center gap-2 group cursor-help">
            <FiInfo size={14} className="text-indigo-500" />
            <span className="text-[10px] font-black text-indigo-600 uppercase tracking-widest">{controls.length} Controles Aplicados</span>
          </div>
        )}
        <div className="h-8 w-px bg-slate-200" />
        <div className="flex flex-col items-end">
           <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Estado</span>
           <span className={`text-xs font-black uppercase ${isAuditMode ? 'text-amber-600' : 'text-emerald-600'}`}>
             {isAuditMode ? 'AUDITORÍA (READ-ONLY)' : 'OPERATIVO'}
           </span>
        </div>
      </div>
    </div>
  );
};
