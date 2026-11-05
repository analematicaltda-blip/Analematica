'use client';

import React from 'react';
import { Button } from '../core/Button';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface EmptyStateProps {
  icon: React.ElementType;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}

const EmptyState: React.FC<EmptyStateProps> = ({ icon: Icon, title, description, actionLabel, onAction, className }) => {
  return (
    <div className={cn("flex flex-col items-center justify-center p-12 text-center bg-[var(--background-card)] rounded-[2rem] border border-dashed border-[var(--border-default)]", className)}>
      <div className="p-6 bg-[var(--background-main)] rounded-full text-[var(--text-muted)] mb-6">
        <Icon size={48} strokeWidth={1.5} />
      </div>
      <h3 className="text-xl font-black text-[var(--text-primary)] uppercase tracking-tight italic mb-2">
        {title}
      </h3>
      <p className="text-sm text-[var(--text-muted)] font-medium max-w-sm mb-8 leading-relaxed">
        {description}
      </p>
      {actionLabel && (
        <Button onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
};

export { EmptyState };
