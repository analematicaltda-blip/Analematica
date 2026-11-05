import React from 'react';
import { Text } from '../atoms/Text';
import { designTokens } from '../tokens/design-tokens';
import { View, Platform, StyleSheet } from 'react-native-web';

interface DataPoint {
  label: string;
  value: number;
}

interface TrendGraphProps {
  title: string;
  data: DataPoint[];
  height?: number;
  color?: string;
}

export const TrendGraph: React.FC<TrendGraphProps> = ({
  title,
  data,
  height = 200,
  color = designTokens.colors.primary
}) => {
  const maxValue = Math.max(...data.map(d => d.value), 1);
  const isWeb = Platform.OS === 'web';

  if (isWeb) {
    return (
      <div style={{
        padding: designTokens.spacing.md,
        backgroundColor: '#fff',
        borderRadius: designTokens.borderRadius.md,
        border: `1px solid ${designTokens.colors.border}`,
        width: '100%',
      }}>
        <Text variant="headingS" style={{ marginBottom: designTokens.spacing.md }}>{title}</Text>
        <div style={{
          display: 'flex',
          alignItems: 'flex-end',
          height: `${height}px`,
          gap: '8px',
          paddingBottom: '20px',
          borderBottom: `1px solid ${designTokens.colors.border}`,
          position: 'relative'
        }}>
          {data.map((point, index) => {
            const barHeight = (point.value / maxValue) * (height - 20);
            return (
              <div key={index} style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                position: 'relative'
              }}>
                <div style={{
                  width: '100%',
                  height: `${barHeight}px`,
                  backgroundColor: color,
                  borderRadius: '4px 4px 0 0',
                }} />
                <div style={{
                  position: 'absolute',
                  bottom: '-20px',
                  fontSize: '10px',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  width: '100%',
                  textAlign: 'center',
                  color: designTokens.colors.textSecondary
                }}>
                  {point.label}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <View style={styles.nativeCard}>
      <Text variant="headingS" style={{ marginBottom: 12 }}>{title}</Text>
      <View style={[styles.chartArea, { height }]}>
        {data.map((point, index) => {
          const barHeight = (point.value / maxValue) * (height - 20);
          return (
            <View key={index} style={styles.barContainer}>
              <View style={[styles.bar, { height: barHeight, backgroundColor: color }]} />
              <Text variant="small" style={styles.barLabel}>{point.label}</Text>
            </View>
          );
        })}
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
    width: '100%',
  },
  chartArea: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 8,
    borderBottomWidth: 1,
    borderBottomColor: designTokens.colors.border,
    paddingBottom: 20,
  },
  barContainer: {
    flex: 1,
    alignItems: 'center',
  },
  bar: {
    width: '100%',
    borderRadius: 2,
  },
  barLabel: {
    position: 'absolute',
    bottom: -18,
    fontSize: 8,
    textAlign: 'center',
  }
});
