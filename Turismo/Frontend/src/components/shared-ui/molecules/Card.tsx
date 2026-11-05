import React from 'react';

export const Card = ({ children, style }: any) => (
  <div style={{
    backgroundColor: '#fff',
    padding: '20px',
    borderRadius: '12px',
    border: '1px solid #e5e7eb',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    ...style
  }}>
    {children}
  </div>
);
