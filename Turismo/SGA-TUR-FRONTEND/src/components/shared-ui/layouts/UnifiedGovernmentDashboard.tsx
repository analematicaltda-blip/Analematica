import React from 'react';
import { TerritorialAnalytics } from '../organisms/TerritorialAnalytics';

export const UnifiedGovernmentDashboard = ({ data }: any) => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '40px' }}>
    <TerritorialAnalytics stats={data.stats} />
    <div style={{ padding: '40px', background: '#f9fafb', borderRadius: '12px', border: '1px dashed #ccc', textAlign: 'center' }}>
      <span style={{ color: '#999' }}>Módulos de Auditoría Avanzada</span>
    </div>
  </div>
);
