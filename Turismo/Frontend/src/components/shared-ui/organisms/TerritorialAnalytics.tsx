import React from 'react';
import { StatCard } from '../molecules/StatCard';

export const TerritorialAnalytics = ({ stats }: any) => (
  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px' }}>
    <StatCard title="Usuarios Totales" value={stats.totalUsers} />
    <StatCard title="Prestadores" value={stats.activeProviders} />
    <StatCard title="Ingresos" value={stats.totalRevenue} />
    <StatCard title="Ocupación" value={stats.occupancyRate} />
  </div>
);
