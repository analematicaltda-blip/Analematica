'use client';

import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, ...props }, ref) => {
    return (
      <div className="w-full space-y-2">
        {label && (
          <label className="block text-xs font-black uppercase tracking-widest text-[var(--text-muted)]">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={cn(
            'flex w-full rounded-[0.75rem] border border-[var(--border-default)] bg-[var(--background-card)] px-4 py-3 text-sm text-[var(--text-primary)] transition-all placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)] focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50',
            error && 'border-[var(--status-error)] focus:ring-[var(--status-error)]',
            className
          )}
          {...props}
        />
        {error && <p className="text-xs font-bold text-[var(--status-error)]">{error}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };
