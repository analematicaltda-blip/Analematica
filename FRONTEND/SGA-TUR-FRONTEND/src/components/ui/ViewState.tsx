'use client';

import React from 'react';
import { Spinner } from '@/components/common/Spinner';
import { AlertCircle, FileQuestion, CheckCircle2, Lock } from 'lucide-react';
import { Button } from './Button';

interface ViewStateProps {
  isLoading?: boolean;
  isSilentLoading?: boolean;
  loadingMessage?: string;
  isEmpty?: boolean;
  emptyMessage?: string;
  emptyAction?: {
    label: string;
    onClick: () => void;
  };
  error?: string | null;
  isDegraded?: boolean;
  errorAction?: {
    label: string;
    onClick: () => void;
  };
  isSuccess?: boolean;
  successMessage?: string;
  isDisabled?: boolean;
  disabledMessage?: string;
  children: React.ReactNode;
}

export const ViewState: React.FC<ViewStateProps> = ({
  isLoading,
  loadingMessage = "Cargando información estratégica...",
  isSilentLoading = false,
  isDegraded = false,
  isEmpty,
  emptyMessage = 'No se encontraron registros en este dominio.',
  emptyAction,
  error,
  errorAction,
  isSuccess,
  successMessage = 'Operación completada con éxito.',
  isDisabled,
  disabledMessage = 'Esta acción requiere un nivel de autoridad superior.',
  children
}) => {
  if (isLoading && !isSilentLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 min-h-[400px] animate-in fade-in duration-500">
        <Spinner text={loadingMessage} />
      </div>
    );
  }

  if (error || isDegraded) {
    return (
      <div className="flex flex-col items-center justify-center p-12 min-h-[400px] text-center animate-in zoom-in-95 duration-300">
        <div className={`w-16 h-16 ${isDegraded ? 'bg-amber-100 text-amber-600' : 'bg-red-100 text-red-600'} rounded-2xl flex items-center justify-center mb-6`}>
          <AlertCircle size={32} />
        </div>
        <h3 className="text-xl font-black text-slate-900 uppercase tracking-tight mb-2">
          {isDegraded ? 'Modo Degradado' :
           (error?.toLowerCase().includes('timeout') || error?.toLowerCase().includes('no respondió')
            ? 'Latencia Excedida'
            : 'Interrupción Institucional')}
        </h3>
        <p className="text-slate-500 max-w-md mb-8">
          {isDegraded
            ? 'Ciertos servicios externos (Voz/IA) no están disponibles temporalmente. La operación core del ERP sigue funcional.'
            : (error?.toLowerCase().includes('timeout')
              ? 'El sistema no respondió a tiempo. La conexión sigue activa, pero el flujo semántico ha sido interrumpido.'
              : error)}
        </p>
        {(errorAction || isDegraded) && (
          <Button
            onClick={errorAction?.onClick || (() => window.location.reload())}
            variant="outline"
            className={`${isDegraded ? 'border-amber-200 text-amber-600 hover:bg-amber-50' : 'border-red-200 text-red-600 hover:bg-red-50'}`}
          >
            {errorAction?.label || 'Sincronizar Sistema'}
          </Button>
        )}
      </div>
    );
  }

  if (isEmpty) {
    return (
      <div className="flex flex-col items-center justify-center p-12 min-h-[400px] text-center animate-in fade-in duration-500">
        <div className="w-16 h-16 bg-slate-100 text-slate-400 rounded-2xl flex items-center justify-center mb-6">
          <FileQuestion size={32} />
        </div>
        <h3 className="text-xl font-black text-slate-900 uppercase tracking-tight mb-2">Dominio Vacío</h3>
        <p className="text-slate-500 max-w-md mb-8">{emptyMessage}</p>
        {emptyAction && (
          <Button onClick={emptyAction.onClick} className="bg-brand text-white font-bold">
            {emptyAction.label}
          </Button>
        )}
      </div>
    );
  }

  if (isDisabled) {
    return (
      <div className="flex flex-col items-center justify-center p-12 min-h-[400px] text-center opacity-60 grayscale animate-in fade-in duration-500">
        <div className="w-16 h-16 bg-slate-200 text-slate-500 rounded-2xl flex items-center justify-center mb-6">
          <Lock size={32} />
        </div>
        <h3 className="text-xl font-black text-slate-900 uppercase tracking-tight mb-2">Acceso Restringido</h3>
        <p className="text-slate-500 max-w-md">{disabledMessage}</p>
      </div>
    );
  }

  return (
    <div className="relative h-full w-full">
      {isSuccess && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-white/80 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="flex flex-col items-center text-center">
            <div className="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mb-4">
              <CheckCircle2 size={32} />
            </div>
            <p className="text-lg font-black text-slate-900 uppercase italic">{successMessage}</p>
          </div>
        </div>
      )}
      {children}
    </div>
  );
};
