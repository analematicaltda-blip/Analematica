'use client';

import React from 'react';
import { AnalyticalDecision } from '../types';
import { FiZap, FiCheck, FiX, FiInfo } from 'react-icons/fi';
import { Button } from '../../ui/components/core/Button';

interface DecisionCardProps {
  decision: AnalyticalDecision;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
}

export const DecisionAssistant = ({ decision, onApprove, onReject }: DecisionCardProps) => {
  const { severity, context, suggestion, impact } = decision;

  const severityColors = {
    low: 'bg-blue-500',
    medium: 'bg-amber-500',
    high: 'bg-orange-500',
    critical: 'bg-rose-500'
  };

  return (
    <div className="bg-[var(--background-card)] rounded-[1.5rem] border border-[var(--border-default)] overflow-hidden shadow-xl animate-in zoom-in-95 duration-500">
      <div className={`h-1.5 ${severityColors[severity]}`} />
      <div className="p-8">
        <div className="flex items-center gap-3 mb-6">
          <div className={`p-2 rounded-lg ${severityColors[severity]} text-white`}>
            <FiZap size={16} />
          </div>
          <span className="text-[10px] font-black uppercase tracking-widest text-[var(--text-muted)]">Recomendación IA Decisora</span>
          <span className={`ml-auto text-[8px] font-black uppercase px-2 py-0.5 rounded-full text-white ${severityColors[severity]}`}>
            {severity}
          </span>
        </div>

        <h3 className="text-xl font-black text-[var(--text-primary)] uppercase tracking-tighter italic mb-4">
          Optimización detectada
        </h3>

        <div className="space-y-6">
          <div className="bg-[var(--background-main)] p-4 rounded-xl border border-[var(--border-default)]">
            <p className="text-[10px] font-black text-indigo-500 uppercase mb-1 flex items-center gap-1">
              <FiInfo /> Contexto
            </p>
            <p className="text-sm text-[var(--text-secondary)] font-medium leading-relaxed italic">
              "{context}"
            </p>
          </div>

          <div className="space-y-2">
            <p className="text-[10px] font-black text-[var(--text-muted)] uppercase tracking-widest">Acción Sugerida</p>
            <p className="text-sm font-bold text-[var(--text-primary)]">{suggestion}</p>
          </div>

          <div className="pt-4 border-t border-[var(--border-default)] flex items-center justify-between">
            <div>
              <p className="text-[9px] font-black text-[var(--text-muted)] uppercase">Impacto Estimado</p>
              <p className="text-lg font-black text-emerald-600">{impact}</p>
            </div>
            <div className="flex gap-2">
              <Button size="sm" variant="outline" onClick={() => onReject(decision.id)}>
                <FiX className="mr-1" /> Ignorar
              </Button>
              <Button size="sm" onClick={() => onApprove(decision.id)}>
                <FiCheck className="mr-1" /> Ejecutar
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
