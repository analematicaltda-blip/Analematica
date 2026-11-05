'use client';

import React from 'react';
import { FiTrendingUp, FiTrendingDown, FiMinus } from 'react-icons/fi';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface KPICardProps {
  label: string;
  value: string | number;
  trend?: {
    value: string | number;
    type: 'up' | 'down' | 'neutral';
  };
  icon?: any;
  statusColor?: string;
  className?: string;
}

export const KPICard = ({ label, value, trend, icon: Icon, statusColor, className }: KPICardProps) => {
  return (
    <div className={cn(
      "bg-[var(--background-card)] p-8 rounded-[1.5rem] border border-[var(--border-default)] shadow-sm hover:shadow-md transition-all duration-300 group",
      className
    )}>
      <div className="flex justify-between items-start mb-6">
        {Icon && (
          <div className={cn(
            "p-4 rounded-2xl bg-[var(--background-main)] text-[var(--brand-primary)] group-hover:scale-110 transition-transform duration-300",
            statusColor && `text-${statusColor}`
          )}>
            <Icon size={28} />
          </div>
        )}
        {trend && (
          <div className={cn(
            "flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter",
            trend.type === 'up' ? "bg-[var(--status-success)]/10 text-[var(--status-success)]" :
            trend.type === 'down' ? "bg-[var(--status-error)]/10 text-[var(--status-error)]" :
            "bg-[var(--status-info)]/10 text-[var(--status-info)]"
          )}>
            {trend.type === 'up' ? <FiTrendingUp /> : trend.type === 'down' ? <FiTrendingDown /> : <FiMinus />}
            {trend.value}
          </div>
        )}
      </div>

      <div>
        <p className="text-[10px] font-black text-[var(--text-muted)] uppercase tracking-[0.2em] mb-1">{label}</p>
        <h3 className="text-3xl font-black text-[var(--text-primary)] tracking-tight">{value}</h3>
      </div>
    </div>
  );
};
