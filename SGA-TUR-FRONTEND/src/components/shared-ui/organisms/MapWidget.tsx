import React from 'react';
import { View, Platform, StyleSheet } from 'react-native-web';
import { designTokens } from '../tokens/design-tokens';
import { Text } from '../atoms/Text';

interface MapWidgetProps {
  regionName: string;
  dataPoints: Array<{ id: string; label: string; value: number }>;
}

export const MapWidget: React.FC<MapWidgetProps> = ({ regionName, dataPoints }) => {
  const isWeb = Platform.OS === 'web';

  if (isWeb) {
    return (
      <div style={{
        height: '400px',
        backgroundColor: '#f0f0f0',
        borderRadius: designTokens.borderRadius.lg,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        border: `1px solid ${designTokens.colors.border}`,
      }}>
        <Text variant="headingM">Mapa de {regionName}</Text>
        <div style={{ marginTop: '20px' }}>
          {dataPoints.map(point => (
            <div key={point.id} style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
              <div style={{
                width: '8px',
                height: '8px',
                backgroundColor: designTokens.colors.primary,
                borderRadius: '50%',
                marginRight: '8px'
              }} />
              <Text variant="caption">{point.label}: {point.value}</Text>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <View style={styles.nativeContainer}>
      <Text variant="headingM">Mapa de {regionName}</Text>
      <View style={{ marginTop: 20 }}>
        {dataPoints.map(point => (
          <View key={point.id} style={styles.row}>
            <View style={styles.dot} />
            <Text variant="caption">{point.label}: {point.value}</Text>
          </View>
        ))}
      </View>
      <View style={styles.placeholder}>
        <Text variant="small" color="textSecondary">[Mapa Interactivo Native Placeholder]</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  nativeContainer: {
    height: 300,
    backgroundColor: '#f0f0f0',
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: designTokens.colors.border,
    padding: 16
  },
  row: { flexDirection: 'row', alignItems: 'center', marginBottom: 4 },
  dot: { width: 8, height: 8, backgroundColor: designTokens.colors.primary, borderRadius: 4, marginRight: 8 },
  placeholder: { marginTop: 20 }
});
