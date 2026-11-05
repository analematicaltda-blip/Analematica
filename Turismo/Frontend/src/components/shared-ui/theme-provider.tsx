import React, { createContext, useContext, useState, ReactNode } from 'react';
import { designTokens } from './tokens/design-tokens';

type ThemeMode = 'light' | 'dark' | 'institutional';

interface ThemeContextType {
  mode: ThemeMode;
  setMode: (mode: ThemeMode) => void;
  tokens: typeof designTokens;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [mode, setMode] = useState<ThemeMode>('light');

  // In a real scenario, this would compute deep overrides for dark mode
  const currentTokens = {
    ...designTokens,
    colors: {
      ...designTokens.colors,
      background: mode === 'dark' ? '#000000' : designTokens.colors.background,
      card: mode === 'dark' ? '#111111' : designTokens.colors.card,
      textPrimary: mode === 'dark' ? '#ffffff' : designTokens.colors.textPrimary,
    }
  };

  return (
    <ThemeContext.Provider value={{ mode, setMode, tokens: currentTokens }}>
      <div style={{
        backgroundColor: currentTokens.colors.background,
        color: currentTokens.colors.textPrimary,
        minHeight: '100vh'
      }}>
        {children}
      </div>
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within a ThemeProvider');
  return context;
};
