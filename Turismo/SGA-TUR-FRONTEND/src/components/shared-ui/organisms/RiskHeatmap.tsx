import React from 'react';
import { Text } from '../atoms/Text';
import { designTokens } from '../tokens/design-tokens';
import { View, Platform, StyleSheet } from 'react-native-web';

interface RiskZone {
  label: string;
  level: number; // 0 to 100
}

interface RiskHeatmapProps {
  zones: RiskZone[];
}

export const RiskHeatmap: React.FC<RiskHeatmapProps> = ({ zones }) => {
  const getLevelColor = (level: number) => {
    if (level > 80) return '#ef4444'; // Red
    if (level > 50) return '#f59e0b'; // Amber
    return '#10b981'; // Green
  };

  const isWeb = Platform.OS === 'web';

  if (isWeb) {
    return (
      <div style={{
        padding: designTokens.spacing.md,
        backgroundColor: '#fff',
        borderRadius: designTokens.borderRadius.md,
        border: `1px solid ${designTokens.colors.border}`,
      }}>
        <Text variant="headingS" style={{ marginBottom: designTokens.spacing.md }}>Mapa de Riesgo Sistémico</Text>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))', gap: '10px' }}>
          {zones.map((zone, index) => (
            <div key={index} style={{
              padding: designTokens.spacing.sm,
              backgroundColor: getLevelColor(zone.level),
              borderRadius: '4px',
              color: '#fff',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center'
            }}>
              <Text variant="caption" style={{ color: '#fff', fontWeight: 600 }}>{zone.label}</Text>
              <Text variant="bodyM" style={{ color: '#fff' }}>{zone.level}%</Text>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <View style={styles.nativeCard}>
      <Text variant="headingS" style={{ marginBottom: 12 }}>Mapa de Riesgo Sistémico</Text>
      <View style={styles.grid}>
        {zones.map((zone, index) => (
          <View key={index} style={[styles.zone, { backgroundColor: getLevelColor(zone.level) }]}>
            <Text variant="caption" style={{ color: '#fff', fontWeight: 'bold' }}>{zone.label}</Text>
            <Text variant="bodyM" style={{ color: '#fff' }}>{zone.level}%</Text>
          </View>
        ))}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  nativeCard: {
    padding: 16,
    backgroundColor: '#ffffff',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: designTokens.colors.border,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  zone: {
    flex: 1,
    minWidth: 100,
    padding: 8,
    borderRadius: 4,
    alignItems: 'center',
    justifyContent: 'center'
  }
});
