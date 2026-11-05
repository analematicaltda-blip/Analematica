import React from 'react';
import { Card } from '../molecules/Card';
import { Text } from '../atoms/Text';
import { Button } from '../atoms/Button';
import { spacing } from '../tokens/spacing';
import { View, Platform, StyleSheet } from 'react-native-web';

interface Report {
  id: string;
  name: string;
  lastGenerated: string;
  type: 'financial' | 'operational' | 'institutional';
}

interface InstitutionalReportsProps {
  reports: Report[];
  onDownload: (id: string) => void;
}

export const InstitutionalReports: React.FC<InstitutionalReportsProps> = ({ reports, onDownload }) => {
  const isWeb = Platform.OS === 'web';

  if (isWeb) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
        <Text variant="headingM">Reportes Institucionales</Text>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: spacing.md
        }}>
          {reports.map(report => (
            <Card key={report.id} padding="md">
              <Text variant="headingM">{report.name}</Text>
              <div style={{ margin: `${spacing.sm}px 0` }}>
                <Text variant="caption" color="textSecondary">Tipo: {report.type.toUpperCase()}</Text>
              </div>
              <div style={{ marginBottom: spacing.md }}>
                <Text variant="small" color="textSecondary">Generado: {report.lastGenerated}</Text>
              </div>
              <Button label="Descargar PDF" variant="secondary" onPress={() => onDownload(report.id)} />
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <View style={styles.nativeContainer}>
      <Text variant="headingM" style={{ marginBottom: 16 }}>Reportes Institucionales</Text>
      <View style={{ gap: 12 }}>
        {reports.map(report => (
          <Card key={report.id} padding="md" style={styles.nativeCard}>
            <Text variant="headingM" style={{ fontSize: 18 }}>{report.name}</Text>
            <View style={{ marginVertical: 8 }}>
              <Text variant="caption" color="textSecondary">Tipo: {report.type.toUpperCase()}</Text>
              <Text variant="small" color="textSecondary">Generado: {report.lastGenerated}</Text>
            </View>
            <Button label="Descargar PDF" variant="secondary" onPress={() => onDownload(report.id)} />
          </Card>
        ))}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  nativeContainer: { paddingVertical: 12 },
  nativeCard: { padding: 16 }
});
