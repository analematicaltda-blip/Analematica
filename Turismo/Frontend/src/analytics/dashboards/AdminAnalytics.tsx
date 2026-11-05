'use client';

import React from 'react';
import { SmartKPIWidget } from '../widgets/SmartKPIWidget';
import { GrowthChart } from '../widgets/GrowthChart';
import { FiGlobe, FiShield, FiZap, FiActivity } from 'react-icons/fi';
import { Badge } from '../../ui/components/core/Badge';

export const AdminAnalytics = ({ data }: { data: any }) => {
  return (
    <div className="space-y-10 animate-in slide-in-from-right-8 duration-700">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <SmartKPIWidget
          label="GTV Global"
          value={data.gtv}
          icon={FiGlobe}
        />
        <SmartKPIWidget
          label="ROI Sistémico"
          value={data.systemic_roi}
          icon={FiZap}
        />
        <SmartKPIWidget
          label="Trust Score IA"
          value={data.ai_trust}
          icon={FiShield}
        />
        <SmartKPIWidget
          label="Salud de Red"
          value={data.network_health}
          icon={FiActivity}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <GrowthChart
            title="Crecimiento Transaccional Regional"
            data={data.growth_series}
            dataKey="value"
            color="#4f46e5"
          />
        </div>
        <div className="bg-[var(--background-card)] p-8 rounded-[1.5rem] border border-[var(--border-default)] shadow-sm">
           <h3 className="text-xl font-black text-[var(--text-primary)] uppercase tracking-tighter italic mb-8">Alertas Decisionales</h3>
           <div className="space-y-4">
              {data.alerts.map((alert: any, i: number) => (
                <div key={i} className="p-4 rounded-xl bg-[var(--background-main)] border border-[var(--border-default)] hover:border-indigo-500/50 transition-all group cursor-pointer">
                   <div className="flex justify-between mb-2">
                      <span className="text-[9px] font-black uppercase text-indigo-500">{alert.domain}</span>
                      <Badge variant={alert.severity === 'high' ? 'destructive' : 'default'} className="text-[8px] px-1.5 py-0">
                         {alert.severity}
                      </Badge>
                   </div>
                   <p className="text-xs font-bold text-[var(--text-primary)] leading-tight">{alert.msg}</p>
                </div>
              ))}
           </div>
        </div>
      </div>
    </div>
  );
};

// Simple badge component as it was missing from core in previous phases or just used via @/components/ui/Badge
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const Badge = ({ children, variant = 'default', className }: any) => {
  const variants: any = {
    default: 'bg-indigo-500/10 text-indigo-600',
    destructive: 'bg-rose-500/10 text-rose-600',
    outline: 'border border-[var(--border-default)] text-[var(--text-muted)]',
  };
  return (
    <span className={cn("px-2 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter", variants[variant], className)}>
      {children}
    </span>
  );
};
