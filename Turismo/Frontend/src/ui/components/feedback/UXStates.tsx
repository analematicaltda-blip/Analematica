'use client';

import React from 'react';
import { FiInbox, FiAlertCircle, FiLock, FiRefreshCw } from 'react-icons/fi';
import { Button } from '../core/Button';

interface StateProps {
  title: string;
  message: string;
  onRetry?: () => void;
  actionLabel?: string;
}

export const EmptyState = ({ title, message, onRetry, actionLabel }: StateProps) => (
  <div className="flex flex-col items-center justify-center py-20 px-8 text-center animate-in fade-in duration-500">
    <div className="w-20 h-20 bg-[var(--background-card)] rounded-[2rem] flex items-center justify-center text-[var(--text-muted)] mb-6 border border-[var(--border-default)] shadow-inner">
      <FiInbox size={32} />
    </div>
    <h3 className="text-xl font-black text-[var(--text-primary)] uppercase tracking-tighter italic mb-2">{title}</h3>
    <p className="text-sm text-[var(--text-muted)] max-w-sm mb-8">{message}</p>
    {onRetry && (
      <Button onClick={onRetry} variant="outline" size="sm">
        {actionLabel || 'Crear Registro'}
      </Button>
    )}
  </div>
);

export const ErrorPanel = ({ title, message, onRetry }: StateProps) => (
  <div className="bg-[var(--status-error)]/5 border border-[var(--status-error)]/20 p-12 rounded-[2rem] text-center animate-in zoom-in-95 duration-500">
    <FiAlertCircle className="mx-auto text-[var(--status-error)] mb-6" size={48} />
    <h3 className="text-xl font-black text-[var(--text-primary)] uppercase tracking-tighter italic mb-2">{title}</h3>
    <p className="text-sm text-[var(--text-muted)] max-w-md mx-auto mb-8">{message}</p>
    {onRetry && (
      <Button onClick={onRetry} variant="destructive" size="sm">
        <FiRefreshCw className="mr-2" /> Reintentar Conexión
      </Button>
    )}
  </div>
);

export const AccessDenied = ({ title, message }: Partial<StateProps>) => (
  <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
    <div className="w-24 h-24 bg-[var(--status-warning)]/10 rounded-full flex items-center justify-center text-[var(--status-warning)] mb-8 animate-pulse">
      <FiLock size={40} />
    </div>
    <h2 className="text-3xl font-black text-[var(--text-primary)] uppercase tracking-tight mb-4">
      {title || 'Acceso Restringido'}
    </h2>
    <p className="text-lg text-[var(--text-muted)] max-w-lg italic">
      {message || 'Su nivel de autoridad actual no le permite visualizar este dominio. Contacte a la Autoridad Soberana si cree que es un error.'}
    </p>
  </div>
);

export const LoadingSkeleton = ({ className }: { className?: string }) => (
  <div className={`animate-pulse bg-[var(--background-card)] rounded-[1.5rem] ${className}`} />
);
