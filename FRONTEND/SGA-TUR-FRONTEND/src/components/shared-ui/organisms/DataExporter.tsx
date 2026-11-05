import React from 'react';
import { Button } from '../atoms/Button';
import { designTokens } from '../tokens/design-tokens';
import { Text } from '../atoms/Text';
import { View, Platform, StyleSheet } from 'react-native-web';

interface DataExporterProps {
  reportName: string;
  onExport: (format: 'pdf' | 'csv' | 'xls') => void;
  isLoading?: boolean;
}

export const DataExporter: React.FC<DataExporterProps> = ({
  reportName,
  onExport,
  isLoading
}) => {
  const isWeb = Platform.OS === 'web';

  if (isWeb) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: designTokens.spacing.md,
        backgroundColor: designTokens.colors.backgroundAlt,
        borderRadius: designTokens.borderRadius.md,
        border: `1px solid ${designTokens.colors.border}`,
        gap: designTokens.spacing.md,
        flexWrap: 'wrap'
      }}>
        <div style={{ flex: 1, minWidth: '200px' }}>
          <Text variant="bodyM" style={{ fontWeight: 600 }}>{reportName}</Text>
          <Text variant="caption">Seleccione el formato para descargar el reporte oficial.</Text>
        </div>
        <div style={{ display: 'flex', gap: designTokens.spacing.sm }}>
          <Button
            variant="secondary"
            onPress={() => onExport('pdf')}
            label="PDF"
            disabled={isLoading}
          />
          <Button
            variant="secondary"
            onPress={() => onExport('csv')}
            label="CSV"
            disabled={isLoading}
          />
          <Button
            variant="primary"
            onPress={() => onExport('xls')}
            label="Excel"
            disabled={isLoading}
          />
        </div>
      </div>
    );
  }

  return (
    <View style={styles.nativeContainer}>
      <Text variant="bodyM" style={{ fontWeight: 'bold' }}>{reportName}</Text>
      <Text variant="caption" style={{ marginBottom: 12 }}>Seleccione el formato para descargar.</Text>
      <View style={styles.row}>
        <Button variant="secondary" label="PDF" onPress={() => onExport('pdf')} disabled={isLoading} />
        <Button variant="secondary" label="CSV" onPress={() => onExport('csv')} disabled={isLoading} />
        <Button variant="primary" label="Excel" onPress={() => onExport('xls')} disabled={isLoading} />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  nativeContainer: {
    padding: 16,
    backgroundColor: designTokens.colors.backgroundAlt,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: designTokens.colors.border,
  },
  row: { flexDirection: 'row', gap: 8, flexWrap: 'wrap' }
});
