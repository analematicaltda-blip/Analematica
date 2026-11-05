import React from 'react';
import { TextInput, Platform, StyleSheet } from 'react-native-web';
import { designTokens } from '../tokens/design-tokens';

interface InputProps {
  placeholder?: string;
  value?: string;
  onChange?: (val: string) => void;
  type?: string;
  style?: any;
}

export const Input: React.FC<InputProps> = ({ placeholder, value, onChange, type = 'text', style }) => {
  if (Platform.OS === 'web') {
    return (
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        style={{
          padding: '12px 16px',
          borderRadius: designTokens.borderRadius.md,
          border: `1px solid ${designTokens.colors.border}`,
          fontSize: '16px',
          width: '100%',
          boxSizing: 'border-box',
          outline: 'none',
          ...style
        }}
      />
    );
  }

  return (
    <TextInput
      placeholder={placeholder}
      value={value}
      onChangeText={onChange}
      secureTextEntry={type === 'password'}
      style={[styles.nativeInput, style]}
    />
  );
};

const styles = StyleSheet.create({
  nativeInput: {
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: designTokens.colors.border,
    fontSize: 16,
    width: '100%',
    backgroundColor: '#ffffff'
  }
});
