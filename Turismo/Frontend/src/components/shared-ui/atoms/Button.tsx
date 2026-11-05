import React from 'react';

interface ButtonProps {
  label: string;
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  onPress?: () => void;
  onClick?: () => void;
  disabled?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  label,
  variant = 'primary',
  onPress,
  onClick,
  disabled
}) => {
  const handlePress = onPress || onClick;

  const getBackgroundColor = () => {
    if (disabled) return '#cccccc';
    switch (variant) {
      case 'primary': return '#1e40af';
      case 'secondary': return '#64748b';
      case 'danger': return '#ef4444';
      case 'ghost': return 'transparent';
      default: return '#1e40af';
    }
  };

  return (
    <button
      onClick={handlePress}
      disabled={disabled}
      style={{
        backgroundColor: getBackgroundColor(),
        color: variant === 'ghost' ? '#1e40af' : '#ffffff',
        padding: '10px 20px',
        borderRadius: '8px',
        border: variant === 'ghost' ? '1px solid #1e40af' : 'none',
        cursor: disabled ? 'not-allowed' : 'pointer',
        fontSize: '16px',
        fontWeight: '600',
      }}
    >
      {label}
    </button>
  );
};
