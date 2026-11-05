'use client';

import React from 'react';
import { AlertTriangle, ShieldAlert, Trash2, CheckCircle } from 'lucide-react';
import { Button } from './Button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from './Dialog';

interface CriticalActionDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  type?: 'danger' | 'warning' | 'sovereign' | 'success';
  isLoading?: boolean;
}

export const CriticalActionDialog: React.FC<CriticalActionDialogProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  confirmLabel = 'Confirmar Acción',
  cancelLabel = 'Cancelar',
  type = 'warning',
  isLoading = false
}) => {
  const icons = {
    danger: <Trash2 className="text-red-600" size={32} />,
    warning: <AlertTriangle className="text-amber-600" size={32} />,
    sovereign: <ShieldAlert className="text-indigo-600" size={32} />,
    success: <CheckCircle className="text-emerald-600" size={32} />
  };

  const colors = {
    danger: 'bg-red-50 border-red-200',
    warning: 'bg-amber-50 border-amber-200',
    sovereign: 'bg-indigo-50 border-indigo-200',
    success: 'bg-emerald-50 border-emerald-200'
  };

  const buttonColors = {
    danger: 'bg-red-600 hover:bg-red-700',
    warning: 'bg-amber-600 hover:bg-amber-700',
    sovereign: 'bg-indigo-600 hover:bg-indigo-700',
    success: 'bg-emerald-600 hover:bg-emerald-700'
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px] rounded-[2.5rem] border-none shadow-2xl p-0 overflow-hidden">
        <div className={`p-8 flex flex-col items-center text-center ${colors[type]}`}>
          <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center shadow-sm mb-6">
            {icons[type]}
          </div>
          <DialogTitle className="text-2xl font-black text-slate-900 uppercase tracking-tighter italic mb-2">
            {title}
          </DialogTitle>
          <DialogDescription className="text-slate-600 font-medium leading-relaxed">
            {description}
          </DialogDescription>
          <div className="mt-6 p-4 bg-white/50 rounded-xl border border-black/5 text-[10px] text-slate-500 font-bold uppercase tracking-wider leading-tight">
            Aviso de Responsabilidad: Al confirmar, usted asume la titularidad legal de esta operación en el registro institucional.
          </div>
        </div>

        <DialogFooter className="p-8 bg-white flex flex-col sm:flex-row gap-3 sm:justify-center">
          <Button variant="outline" onClick={onClose} disabled={isLoading} className="rounded-xl font-bold border-slate-200">
            {cancelLabel}
          </Button>
          <Button
            onClick={onConfirm}
            disabled={isLoading}
            className={`rounded-xl font-black uppercase tracking-widest text-white shadow-lg transition-all ${buttonColors[type]} px-8`}
          >
            {isLoading ? 'Procesando...' : confirmLabel}
          </Button>
        </DialogFooter>

        {type === 'sovereign' && (
          <div className="bg-slate-900 px-8 py-3 flex items-center justify-center gap-2">
             <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-pulse" />
             <span className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.3em]">Validación de Autoridad Requerida</span>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};
