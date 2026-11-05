export const colors = {
  primary: '#0070f3',
  secondary: '#666666',
  success: '#0070f3', // Aligning with SARITA primary branding
  warning: '#f5a623',
  danger: '#ff0000',
  background: '#ffffff',
  textPrimary: '#111111',
  textSecondary: '#666666',
  border: '#eaeaea',
  card: '#fafafa',
} as const;

export const designTokens = {
  colors,
  borderRadius: {
    sm: 4,
    md: 8,
    lg: 12,
    full: 9999,
  },
  shadows: {
    sm: '0 2px 4px rgba(0,0,0,0.1)',
    md: '0 4px 8px rgba(0,0,0,0.1)',
  },
};
