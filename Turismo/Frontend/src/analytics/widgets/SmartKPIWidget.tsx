'use client';

import React from 'react';
import { KPIValue } from '../../types';
import { FiTrendingUp, FiTrendingDown, FiMinus } from 'react-icons/fi';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface SmartKPIWidgetProps {
  label: string;
  value: KPIValue;
  icon?: any;
  className?: string;
}

export const SmartKPIWidget = ({ label, value, icon: Icon, className }: SmartKPIWidgetProps) => {
  const { current, trend, unit } = value;
  const isCurrency = unit === '$';

  const formattedValue = isCurrency
    ? `$${current.toLocaleString('es-CO', { minimumFractionDigits: 0 })}`
    : `${current}${unit}`;

  return (
    <div className={cn(
      "bg-[var(--background-card)] p-8 rounded-[1.5rem] border border-[var(--border-default)] shadow-sm hover:shadow-md transition-all duration-300 group",
      className
    )}>
      <div className="flex justify-between items-start mb-6">
        {Icon && (
          <div className="p-4 rounded-2xl bg-[var(--background-main)] text-[var(--brand-primary)] group-hover:scale-110 transition-transform duration-300">
            <Icon size={28} />
          </div>
        )}
        {trend && (
          <div className={cn(
            "flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter",
            trend.direction === 'up' ? "bg-emerald-500/10 text-emerald-600" :
            trend.direction === 'down' ? "bg-rose-500/10 text-rose-600" :
            "bg-slate-500/10 text-slate-600"
          )}>
            {trend.direction === 'up' ? <FiTrendingUp /> : trend.direction === 'down' ? <FiTrendingDown /> : <FiMinus />}
            {trend.value}%
          </div>
        )}
      </div>

      <div>
        <p className="text-[10px] font-black text-[var(--text-muted)] uppercase tracking-[0.2em] mb-1">{label}</p>
        <h3 className="text-3xl font-black text-[var(--text-primary)] tracking-tight">{formattedValue}</h3>
        {trend && (
          <p className="text-[10px] text-[var(--text-muted)] mt-2 italic">{trend.label}</p>
        )}
      </div>
    </div>
  );
};
