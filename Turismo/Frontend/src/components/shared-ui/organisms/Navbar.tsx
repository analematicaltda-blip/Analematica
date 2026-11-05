import React from 'react';
import { designTokens } from '../tokens/design-tokens';
import { spacing } from '../tokens/spacing';
import { Text } from '../atoms/Text';

interface NavbarProps {
  title: string;
  userEmail?: string;
}

export const Navbar: React.FC<NavbarProps> = ({ title, userEmail }) => {
  return (
    <nav style={{
      height: '64px',
      backgroundColor: designTokens.colors.background,
      borderBottom: `1px solid ${designTokens.colors.border}`,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: `0 ${spacing.md}px`,
      width: '100%',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      <Text variant="headingM">{title}</Text>
      {userEmail && <Text variant="caption">{userEmail}</Text>}
    </nav>
  );
};
