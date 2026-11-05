'use client';

import React from 'react';

interface FunnelStep {
  name: string;
  value: number;
  label: string;
}

interface FunnelChartProps {
  steps: FunnelStep[];
  title: string;
}

export const FunnelChart = ({ steps, title }: FunnelChartProps) => {
  const maxValue = steps[0]?.value || 1;

  return (
    <div className="bg-[var(--background-card)] p-8 rounded-[1.5rem] border border-[var(--border-default)] shadow-sm">
      <h3 className="text-xl font-black text-[var(--text-primary)] uppercase tracking-tighter italic mb-8">{title}</h3>
      <div className="space-y-6">
        {steps.map((step, idx) => {
          const width = (step.value / maxValue) * 100;
          const drop = idx > 0 ? (((steps[idx-1].value - step.value) / steps[idx-1].value) * 100).toFixed(0) : 0;

          return (
            <div key={idx} className="relative">
              {idx > 0 && (
                <div className="absolute -top-4 right-0 text-[9px] font-black text-rose-500 uppercase tracking-widest">
                  Leakage: {drop}%
                </div>
              )}
              <div className="flex justify-between items-center mb-2">
                <span className="text-[10px] font-black text-[var(--text-muted)] uppercase tracking-widest">{step.name}</span>
                <span className="text-xs font-bold text-[var(--text-primary)]">{step.label}</span>
              </div>
              <div className="h-10 bg-[var(--background-main)] rounded-xl overflow-hidden flex items-center px-1">
                <div
                  className="h-8 bg-[var(--brand-primary)] rounded-lg transition-all duration-1000 flex items-center justify-end px-3"
                  style={{ width: `${width}%` }}
                >
                  <span className="text-[10px] font-black text-white">{Math.round(width)}%</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
