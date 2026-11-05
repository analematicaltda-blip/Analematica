import React from 'react';
import { Card } from '../molecules/Card';
import { Text } from '../atoms/Text';
import { View, Platform, StyleSheet } from 'react-native-web';
import { designTokens } from '../tokens/design-tokens';

interface PayrollData {
  totalEmployees: number;
  totalPayable: string;
  nextPaymentDate: string;
  pendingLiquidations: number;
}

interface PayrollSnapshotProps {
  data: PayrollData;
}

export const PayrollSnapshot: React.FC<PayrollSnapshotProps> = ({ data }) => {
  const isWeb = Platform.OS === 'web';

  const content = (
    <>
      <Text variant="headingS" style={{ marginBottom: 16 }}>Resumen de Nómina</Text>
      {isWeb ? (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div>
            <Text variant="caption" color="textSecondary">Total Empleados</Text>
            <Text variant="headingM">{data.totalEmployees}</Text>
          </div>
          <div>
            <Text variant="caption" color="textSecondary">Próximo Pago</Text>
            <Text variant="body">{data.nextPaymentDate}</Text>
          </div>
          <div>
            <Text variant="caption" color="textSecondary">Total a Pagar</Text>
            <Text variant="headingM" color="primary">{data.totalPayable}</Text>
          </div>
          <div>
            <Text variant="caption" color="textSecondary">Liquidaciones Pendientes</Text>
            <Text variant="body" color={data.pendingLiquidations > 0 ? 'danger' : 'textPrimary'}>
              {data.pendingLiquidations}
            </Text>
          </div>
        </div>
      ) : (
        <View style={styles.nativeGrid}>
           <View style={styles.stat}>
             <Text variant="caption" color="textSecondary">Total Empleados</Text>
             <Text variant="headingM">{data.totalEmployees}</Text>
           </View>
           <View style={styles.stat}>
             <Text variant="caption" color="textSecondary">Total a Pagar</Text>
             <Text variant="headingM" color="primary">{data.totalPayable}</Text>
           </View>
           <View style={styles.stat}>
             <Text variant="caption" color="textSecondary">Próximo Pago</Text>
             <Text variant="body">{data.nextPaymentDate}</Text>
           </View>
           <View style={styles.stat}>
             <Text variant="caption" color="textSecondary">Liquidaciones</Text>
             <Text variant="body">{data.pendingLiquidations}</Text>
           </View>
        </View>
      )}
    </>
  );

  return <Card>{content}</Card>;
};

const styles = StyleSheet.create({
  nativeGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 16 },
  stat: { width: '45%' }
});
