'use client';

import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { FiX } from 'react-icons/fi';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  className?: string;
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children, className }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
      <div
        className={cn(
          "bg-[var(--background-card)] w-full max-w-lg rounded-[1.5rem] shadow-2xl border border-[var(--border-default)] overflow-hidden animate-in zoom-in-95 duration-300",
          className
        )}
      >
        <div className="flex items-center justify-between p-6 border-b border-[var(--border-default)]">
          {title ? (
            <h3 className="text-xl font-black text-[var(--text-primary)] uppercase tracking-tighter italic">
              {title}
            </h3>
          ) : <div />}
          <button
            onClick={onClose}
            className="p-2 text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors rounded-lg hover:bg-[var(--background-main)]"
          >
            <FiX size={20} />
          </button>
        </div>
        <div className="p-8">
          {children}
        </div>
      </div>
    </div>
  );
};

export { Modal };
