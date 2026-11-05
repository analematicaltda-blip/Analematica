import React from 'react';
import { Card } from '../molecules/Card';
import { Text } from '../atoms/Text';

interface Provider {
  id: string;
  name: string;
  category: string;
  status: 'active' | 'inactive';
  lastActivity: string;
}

interface ProviderMonitoringProps {
  providers: Provider[];
  viewMode: 'table' | 'list';
}

export const ProviderMonitoring: React.FC<ProviderMonitoringProps> = ({ providers, viewMode }) => {
  if (viewMode === 'table') {
    return (
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', backgroundColor: '#fff', border: '1px solid #e5e7eb' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #eaeaea', textAlign: 'left', backgroundColor: '#f9fafb' }}>
              <th style={{ padding: '12px' }}>Nombre</th>
              <th style={{ padding: '12px' }}>Categoría</th>
              <th style={{ padding: '12px' }}>Estado</th>
            </tr>
          </thead>
          <tbody>
            {providers.map(p => (
              <tr key={p.id} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: '12px' }}><Text>{p.name}</Text></td>
                <td style={{ padding: '12px' }}><Text variant="caption">{p.category}</Text></td>
                <td style={{ padding: '12px' }}>
                  <Text color={p.status === 'active' ? 'success' : 'danger'}>{p.status}</Text>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {providers.map(p => (
        <Card key={p.id} padding="sm">
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <Text variant="headingS">{p.name}</Text>
            <Text variant="small" color={p.status === 'active' ? 'success' : 'danger'}>
              {p.status.toUpperCase()}
            </Text>
          </div>
          <Text variant="caption">{p.category}</Text>
        </Card>
      ))}
    </div>
  );
};
