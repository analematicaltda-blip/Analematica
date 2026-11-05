import React from 'react';
import { StatCard } from '../molecules/StatCard';

interface StatGridProps {
  children: React.ReactNode;
  columns?: number;
}

export const StatGrid: React.FC<StatGridProps> = ({ children, columns = 4 }) => {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: `repeat(${columns}, 1fr)`,
      gap: '16px',
      width: '100%',
    }}>
      {children}
    </div>
  );
};
