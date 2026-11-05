'use client';

import React from 'react';
import { FiCheck, FiX, FiAlertTriangle } from 'react-icons/fi';
import { Button } from '../core/Button';

interface VoiceConfirmationProps {
  isOpen: boolean;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export const VoiceConfirmation = ({ isOpen, message, onConfirm, onCancel }: VoiceConfirmationProps) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/40 backdrop-blur-md animate-in fade-in duration-300">
      <div className="bg-[var(--background-card)] w-full max-w-sm rounded-[2rem] shadow-2xl border border-amber-500/20 overflow-hidden animate-in zoom-in-95 duration-300">
        <div className="h-1.5 bg-amber-500" />
        <div className="p-8 text-center">
          <div className="w-16 h-16 bg-amber-500/10 rounded-2xl flex items-center justify-center text-amber-600 mx-auto mb-6">
            <FiAlertTriangle size={32} />
          </div>

          <h3 className="text-xl font-black text-[var(--text-primary)] uppercase tracking-tighter italic mb-4">
            Confirmación Verbal
          </h3>

          <p className="text-sm text-[var(--text-secondary)] font-medium leading-relaxed mb-8">
            {message}
          </p>

          <div className="grid grid-cols-2 gap-3">
            <Button variant="outline" onClick={onCancel} className="w-full">
              <FiX className="mr-2" /> Cancelar
            </Button>
            <Button onClick={onConfirm} className="w-full bg-amber-500 hover:bg-amber-600 shadow-amber-500/20">
              <FiCheck className="mr-2" /> Confirmar
            </Button>
          </div>

          <p className="mt-6 text-[10px] font-black uppercase text-[var(--text-muted)] tracking-widest animate-pulse">
            O di "Confirmo" para ejecutar
          </p>
        </div>
      </div>
    </div>
  );
};
