import React from 'react';
import { Card } from '../molecules/Card';
import { Text } from '../atoms/Text';

interface AlertCardProps {
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
}

export const AlertCard: React.FC<AlertCardProps> = ({ title, description, priority, timestamp }) => {
  const getPriorityColor = () => {
    switch (priority) {
      case 'critical': return '#ef4444';
      case 'high': return '#f59e0b';
      case 'medium': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  return (
    <Card padding="sm">
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
        <Text variant="headingS">{title}</Text>
        <div style={{ backgroundColor: getPriorityColor(), width: '12px', height: '12px', borderRadius: '50%' }} />
      </div>
      <Text variant="caption">{description}</Text>
      <div style={{ marginTop: '8px', textAlign: 'right' }}>
        <Text variant="small" color="textSecondary">{timestamp}</Text>
      </div>
    </Card>
  );
};
