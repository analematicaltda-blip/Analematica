import React from 'react';
import { AlertCard } from '../molecules/AlertCard';
import { Text } from '../atoms/Text';

interface Alert {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
}

interface AlertSystemProps {
  alerts: Alert[];
}

export const AlertSystem: React.FC<AlertSystemProps> = ({ alerts }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Text variant="headingM">Alertas del Sistema</Text>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {alerts.map(alert => (
          <AlertCard
            key={alert.id}
            title={alert.title}
            description={alert.description}
            priority={alert.priority}
            timestamp={alert.timestamp}
          />
        ))}
      </div>
    </div>
  );
};
