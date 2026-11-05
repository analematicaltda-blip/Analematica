"use client";

import React from 'react';
import AtractivosManager from '@/components/AtractivosManager';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';

export default function GestionAtractivosPage() {
  const { user, isLoading, isAuthenticated } = useAuth();
  const router = useRouter();

  // Proteger la ruta para que solo sea accesible por roles autorizados
  React.useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    } else if (!isLoading && user) {
      const allowedRoles = ['ADMIN', 'FUNCIONARIO_DIRECTIVO', 'FUNCIONARIO_PROFESIONAL', 'PRESTADOR']; // Prestadores (guías) también pueden acceder
      if (!allowedRoles.includes(user.role.toUpperCase())) {
        router.push('/dashboard');
      }
    }
  }, [isAuthenticated, isLoading, user, router]);

  // Mostrar un estado de carga mientras se verifica la autenticación
  if (isLoading || !user) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-lg text-gray-500">Cargando...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-gray-900">Gestión de Atractivos Turísticos</h1>
        <p className="mt-2 text-lg text-gray-600">
          Administra los atractivos turísticos del sistema.
        </p>
      </header>

      <div className="bg-white p-4 sm:p-6 lg:p-8 rounded-2xl shadow-lg">
        <AtractivosManager />
      </div>
    </div>
  );
}