import React from 'react';

interface AlertProps {
  children: React.ReactNode;
  variant?: 'info' | 'error' | 'warning' | 'success';
  type?: 'info' | 'error' | 'warning' | 'success';
  title?: string;
}

export function Alert({ children, variant, type, title }: AlertProps) {
  const activeVariant = variant || type || 'info';
  const variants = {
    info: 'bg-blue-100 text-blue-800 border-blue-200',
    error: 'bg-red-100 text-red-800 border-red-200',
    warning: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    success: 'bg-green-100 text-green-800 border-green-200',
  };

  return (
    <div className={`p-4 border rounded-md ${variants[activeVariant]}`}>
      {title && <h4 className="font-bold mb-2">{title}</h4>}
      {children}
    </div>
  );
}
export default Alert;
