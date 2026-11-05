'use client';

import React from 'react';
import { SmartKPIWidget } from '../widgets/SmartKPIWidget';
import { GrowthChart } from '../widgets/GrowthChart';
import { FunnelChart } from '../widgets/FunnelChart';
import { FiDollarSign, FiZap, FiTrendingUp, FiActivity } from 'react-icons/fi';

export const PrestadorAnalytics = ({ data }: { data: any }) => {
  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <SmartKPIWidget
          label="Ingresos Mes"
          value={data.monthly_revenue}
          icon={FiDollarSign}
        />
        <SmartKPIWidget
          label="Tasa Conversión"
          value={data.conversion_rate}
          icon={FiZap}
        />
        <SmartKPIWidget
          label="Margen Bruto"
          value={data.gross_margin}
          icon={FiTrendingUp}
        />
        <SmartKPIWidget
          label="SLA Operativo"
          value={data.sla}
          icon={FiActivity}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <GrowthChart
            title="Tendencia de Ingresos vs Costos"
            data={data.revenue_series}
            dataKey="value"
          />
        </div>
        <div>
          <FunnelChart
            title="Eficiencia del Embudo"
            steps={data.funnel_steps}
          />
        </div>
      </div>
    </div>
  );
};
