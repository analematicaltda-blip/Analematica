import React from 'react';

export const Text = ({ children, variant, style }: any) => {
  const styles: any = {
    headingL: { fontSize: '32px', fontWeight: 'bold' },
    headingM: { fontSize: '24px', fontWeight: 'bold' },
    headingS: { fontSize: '18px', fontWeight: 'bold' },
    body: { fontSize: '16px' },
    caption: { fontSize: '14px', color: '#6b7280' }
  };
  const base = styles[variant] || styles.body;
  return <span style={{ ...base, ...style }}>{children}</span>;
};
