'use client';

import React, { ReactNode } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';

interface AuthGuardProps {
  children: ReactNode;
  allowedRoles: string[];
}

export const AuthGuard = ({ children, allowedRoles }: AuthGuardProps) => {
  const { user, isLoading, isAuthenticated } = useAuth();
  const router = useRouter();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl font-semibold">Cargando...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Redirigir a login si no está autenticado
    router.push('/login');
    return null; // No renderizar nada mientras se redirige
  }

  if (user && !allowedRoles.includes(user.role)) {
    // Redirigir a una página de 'no autorizado' si el rol no coincide
    router.push('/dashboard'); // O una página específica de acceso denegado
    return (
        <div className="flex items-center justify-center h-screen">
            <div className="text-xl font-semibold text-red-500">Acceso Denegado</div>
        </div>
    );
  }

  return <>{children}</>;
};