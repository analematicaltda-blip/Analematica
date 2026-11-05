'use client';

import React from 'react';
import { FiShieldOff } from 'react-icons/fi';
import { Button } from '../core/Button';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const AccessDenied: React.FC = () => {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-12 text-center bg-[var(--background-main)]">
      <div className="w-24 h-24 bg-slate-100 dark:bg-brand-deep/20 rounded-full flex items-center justify-center text-slate-400 mb-8 border border-[var(--border-default)]">
        <FiShieldOff size={48} />
      </div>
      <h2 className="text-3xl font-black text-[var(--text-primary)] uppercase tracking-tighter italic mb-4">
        Acceso Restringido
      </h2>
      <p className="text-sm font-medium text-[var(--text-muted)] max-w-md mb-10 leading-relaxed">
        Su rol actual no posee los niveles de autoridad requeridos por el Governance Kernel para acceder a este dominio estratégico.
      </p>
      <div className="flex gap-4">
        <Button variant="outline" onClick={() => window.history.back()}>
          Volver atrás
        </Button>
        <Button onClick={() => window.location.href = '/dashboard'}>
          Dashboard Central
        </Button>
      </div>
    </div>
  );
};

export { AccessDenied };
