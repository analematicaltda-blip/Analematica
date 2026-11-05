'use client';

import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'destructive' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', isLoading, children, disabled, ...props }, ref) => {
    const variants = {
      primary: 'bg-[var(--action-primary)] text-[var(--text-on-brand)] hover:opacity-90',
      secondary: 'bg-[var(--action-secondary)] text-[var(--text-on-brand)] hover:opacity-90',
      destructive: 'bg-[var(--action-destructive)] text-[var(--text-on-brand)] hover:opacity-90',
      outline: 'border border-[var(--border-default)] text-[var(--text-primary)] hover:bg-[var(--background-card)]',
      ghost: 'text-[var(--text-primary)] hover:bg-[var(--background-card)]',
    };

    const sizes = {
      sm: 'px-3 py-1.5 text-xs',
      md: 'px-6 py-3 text-sm font-bold',
      lg: 'px-8 py-4 text-lg font-black',
    };

    return (
      <button
        ref={ref}
        disabled={isLoading || disabled}
        className={cn(
          'inline-flex items-center justify-center rounded-[0.75rem] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed active:scale-95',
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      >
        {isLoading ? (
          <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
        ) : null}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button };
