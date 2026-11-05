import React from 'react';
import { Card } from '../molecules/Card';
import { Text } from '../atoms/Text';
import { designTokens } from '../tokens/design-tokens';
import { View, Platform, StyleSheet } from 'react-native-web';

interface InventoryItem {
  id: string;
  name: string;
  stock: number;
  minStock: number;
  unit: string;
}

interface InventoryWidgetProps {
  items: InventoryItem[];
}

export const InventoryWidget: React.FC<InventoryWidgetProps> = ({ items }) => {
  const isWeb = Platform.OS === 'web';

  const renderItem = (item: InventoryItem) => {
    const isLowStock = item.stock <= item.minStock;

    if (isWeb) {
      return (
        <div key={item.id} style={{
          display: 'flex',
          justifyContent: 'space-between',
          padding: '8px 0',
          borderBottom: `1px solid ${designTokens.colors.border}`
        }}>
          <Text variant="body">{item.name}</Text>
          <div style={{ textAlign: 'right' }}>
            <Text variant="body" color={isLowStock ? 'danger' : 'textPrimary'}>
              {item.stock} {item.unit}
            </Text>
            {isLowStock && <div style={{ fontSize: '10px', color: '#ef4444' }}>Stock Bajo</div>}
          </div>
        </div>
      );
    }

    return (
      <View key={item.id} style={styles.nativeItem}>
        <Text variant="body">{item.name}</Text>
        <View style={{ alignItems: 'flex-end' }}>
          <Text variant="body" color={isLowStock ? 'danger' : 'textPrimary'}>
            {item.stock} {item.unit}
          </Text>
          {isLowStock && <Text variant="small" style={{ color: '#ef4444' }}>Stock Bajo</Text>}
        </View>
      </View>
    );
  };

  return (
    <Card>
      <Text variant="headingS" style={{ marginBottom: 12 }}>Estado de Inventario</Text>
      {isWeb ? (
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          {items.map(renderItem)}
        </div>
      ) : (
        <View style={styles.nativeContainer}>
          {items.map(renderItem)}
        </View>
      )}
    </Card>
  );
};

const styles = StyleSheet.create({
  nativeContainer: { flexDirection: 'column' },
  nativeItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: designTokens.colors.border
  }
});
