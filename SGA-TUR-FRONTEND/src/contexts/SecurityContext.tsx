'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { FiShield, FiAlertTriangle, FiLock } from 'react-icons/fi';

interface SecurityState {
  isBlocked: boolean;
  reason: string | null;
  threatLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
}

const SecurityContext = createContext<{
  state: SecurityState;
  reportAnomaly: (anomaly: string) => void;
}>({
  state: { isBlocked: false, reason: null, threatLevel: 'LOW' },
  reportAnomaly: () => {},
});

export const SecurityProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<SecurityState>({
    isBlocked: false,
    reason: null,
    threatLevel: 'LOW',
  });

  const reportAnomaly = (anomaly: string) => {
    console.warn(`[SECURITY ANOMALY] ${anomaly}`);
    // En producción esto enviaría una señal al backend
    if (anomaly.includes('DOM_MUTATION')) {
      setState(prev => ({
        ...prev,
        isBlocked: true,
        reason: anomaly,
        threatLevel: 'CRITICAL'
      }));
    }
  };

  useEffect(() => {
    // Monitor de Mutación del DOM (Anti-Tamper)
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList' && (mutation.target as HTMLElement).id === 'main-nav') {
          reportAnomaly('DOM_MUTATION_DETECTED_IN_NAV');
        }
      });
    });

    observer.observe(document.body, { childList: true, subtree: true });
    return () => observer.disconnect();
  }, []);

  if (state.isBlocked) {
    return (
      <div className="fixed inset-0 bg-black flex flex-col items-center justify-center text-white z-[9999]">
        <FiLock className="text-6xl text-red-500 mb-4 animate-pulse" />
        <h1 className="text-2xl font-bold mb-2">ACCESO RESTRINGIDO POR SEGURIDAD SISTÉMICA</h1>
        <p className="text-gray-400 max-w-md text-center">
          Se ha detectado una actividad inusual. El sistema ha activado el protocolo de aislamiento soberano.
        </p>
        <p className="mt-4 text-xs font-mono text-red-400">ID: {state.reason || 'SEC-ERR-403'}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-8 px-6 py-2 bg-teal-600 hover:bg-teal-700 rounded transition-colors"
        >
          Reintentar Autenticación
        </button>
      </div>
    );
  }

  return (
    <SecurityContext.Provider value={{ state, reportAnomaly }}>
      {children}
    </SecurityContext.Provider>
  );
};

export const useSecurity = () => useContext(SecurityContext);
