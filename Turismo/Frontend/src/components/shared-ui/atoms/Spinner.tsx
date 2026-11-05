import React from 'react';
import { View, ActivityIndicator, Platform, StyleSheet } from 'react-native-web';
import { designTokens } from '../tokens/design-tokens';

export const Spinner: React.FC = () => {
  if (Platform.OS === 'web') {
    return (
      <div style={{
        width: '24px',
        height: '24px',
        border: `3px solid ${designTokens.colors.border}`,
        borderTop: `3px solid ${designTokens.colors.primary}`,
        borderRadius: '50%',
      }} />
    );
  }

  return (
    <View style={styles.container}>
      <ActivityIndicator size="small" color={designTokens.colors.primary} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { padding: 10 }
});
