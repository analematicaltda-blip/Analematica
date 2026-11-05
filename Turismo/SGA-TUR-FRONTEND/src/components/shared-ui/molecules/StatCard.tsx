import React from 'react';
import { Card } from '../molecules/Card';
import { Text } from '../atoms/Text';

export const StatCard = ({ title, value }: any) => (
  <Card>
    <Text variant="caption">{title}</Text>
    <div style={{ marginTop: '5px' }}>
      <Text variant="headingM">{value}</Text>
    </div>
  </Card>
);
