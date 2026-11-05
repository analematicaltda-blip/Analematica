'use client';

import React, { useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { useSecurity } from '@/contexts/SecurityContext';

export const SecurityShield: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { reportAnomaly } = useSecurity();

  useEffect(() => {
    // 1. Detección de mutaciones ilegítimas del DOM (Defensa S-0.2)
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        // Detectar si se inyectan scripts o se modifican elementos críticos fuera de React
        if (mutation.type === 'childList') {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeName === 'SCRIPT' || node.nodeName === 'IFRAME') {
              console.error('ALERTA DE SEGURIDAD: Inyección de nodo no autorizada detectada.');
              reportAnomaly(`DOM_MUTATION_DETECTED:${node.nodeName}`);
              toast.error('INTERVENCIÓN SOBERANA: Se ha detectado una mutación no autorizada del DOM. La sesión ha sido congelada por seguridad.');
            }
          });
        }
      });
    });

    observer.observe(document.documentElement, {
      childList: true,
      subtree: true,
    });

    // 2. Bloqueo de teclas de inspección (Básico)
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'J' || e.key === 'C')) {
        // e.preventDefault();
        console.warn('S-0: Acceso a herramientas de desarrollo monitoreado.');
      }
    };
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      observer.disconnect();
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  return <>{children}</>;
};
