'use client';

import React from 'react';
import { Button } from '../core/Button';
import { FiAlertCircle } from 'react-icons/fi';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface ErrorPanelProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}

const ErrorPanel: React.FC<ErrorPanelProps> = ({ title = "Error de Sistema", message, onRetry, className }) => {
  return (
    <div className={cn("p-12 bg-red-500/5 rounded-[2rem] border border-red-500/20 text-center flex flex-col items-center", className)}>
      <div className="w-16 h-16 bg-red-500/10 text-[var(--status-error)] rounded-2xl flex items-center justify-center mb-6">
        <FiAlertCircle size={32} />
      </div>
      <h3 className="text-xl font-black text-[var(--text-primary)] uppercase tracking-tighter italic mb-2">
        {title}
      </h3>
      <p className="text-sm font-medium text-[var(--text-muted)] max-w-sm mb-8 leading-relaxed">
        {message}
      </p>
      {onRetry && (
        <Button variant="outline" onClick={onRetry} className="border-red-500/20 hover:bg-red-500/10 text-[var(--status-error)]">
          Reintentar Operación
        </Button>
      )}
    </div>
  );
};

export { ErrorPanel };
