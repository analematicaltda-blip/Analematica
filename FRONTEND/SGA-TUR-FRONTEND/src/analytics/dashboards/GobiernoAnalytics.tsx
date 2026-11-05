'use client';

import React from 'react';
import { SmartKPIWidget } from '../widgets/SmartKPIWidget';
import { GrowthChart } from '../widgets/GrowthChart';
import { FiUsers, FiTrendingUp, FiMapPin, FiBarChart2 } from 'react-icons/fi';

export const GobiernoAnalytics = ({ data }: { data: any }) => {
  return (
    <div className="space-y-10 animate-in slide-in-from-bottom-8 duration-700">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <SmartKPIWidget
          label="Empleos Generados"
          value={data.jobs_total}
          icon={FiUsers}
        />
        <SmartKPIWidget
          label="Impacto Económico"
          value={data.economic_impact}
          icon={FiTrendingUp}
        />
        <SmartKPIWidget
          label="Nodos Activos"
          value={data.active_nodes}
          icon={FiMapPin}
        />
        <SmartKPIWidget
          label="Tasa Crecimiento"
          value={data.growth_rate}
          icon={FiBarChart2}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <GrowthChart
            title="Evolución de Recaudación Regional"
            data={data.tax_series}
            dataKey="value"
            color="#10b981"
          />
        </div>
        <div className="bg-[var(--background-card)] p-8 rounded-[1.5rem] border border-[var(--border-default)] shadow-sm">
           <h3 className="text-xl font-black text-[var(--text-primary)] uppercase tracking-tighter italic mb-8">Participación por Sector</h3>
           <div className="space-y-6">
              {data.sectors.map((sector: any, i: number) => (
                <div key={i}>
                   <div className="flex justify-between text-[10px] font-black uppercase mb-2">
                      <span className="text-[var(--text-muted)]">{sector.name}</span>
                      <span className="text-[var(--text-primary)]">{sector.percent}%</span>
                   </div>
                   <div className="h-2 bg-[var(--background-main)] rounded-full overflow-hidden">
                      <div
                        className="h-full bg-emerald-500 rounded-full transition-all duration-1000"
                        style={{ width: `${sector.percent}%` }}
                      />
                   </div>
                </div>
              ))}
           </div>
        </div>
      </div>
    </div>
  );
};
