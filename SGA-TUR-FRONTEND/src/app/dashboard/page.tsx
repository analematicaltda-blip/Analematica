'use client';

import React, { useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useDashboard } from '@/contexts/DashboardContext';
import { useRouter } from 'next/navigation';

// --- Importación de Componentes de Vista ---
import WelcomeDashboard from '@/components/agent/WelcomeDashboard'; // Un componente de bienvenida genérico
import StatisticsDashboard from '@/components/StatisticsDashboard';
import AdminDashboard from '@/components/AdminDashboard';
import FormList from '@/components/FormList';
import PublicacionManager from '@/components/PublicacionManager';
import AtractivosManager from '@/components/AtractivosManager';
import PrestadorManager from '@/components/PrestadorManager';
import ArtesanosManager from '@/components/ArtesanosManager'; // Asegurarse de que esté importado
import UserManager from '@/components/UserManager';
import FormManager from '@/components/FormManager';
import VerificacionManager from '@/components/VerificacionManager';
import SiteConfigManager from '@/components/SiteConfigManager';

// --- Mapeo de Vistas a Componentes ---
// Corregido y completado para incluir todos los paneles necesarios.
const viewComponents: { [key: string]: React.ComponentType } = {
  'inicio': WelcomeDashboard,
  '/dashboard/estadisticas': StatisticsDashboard,
  '/dashboard/analytics': AdminDashboard,
  '/dashboard/mis-formularios': FormList,
  '/dashboard/publicaciones': PublicacionManager,
  '/dashboard/atractivos': AtractivosManager,
  '/dashboard/prestadores': PrestadorManager, // Vista para Prestadores
  '/dashboard/artesanos': ArtesanosManager,   // Vista para Artesanos
  '/dashboard/usuarios': UserManager,
  '/dashboard/formularios': FormManager,
  '/dashboard/verificacion': VerificacionManager,
  '/dashboard/configuracion': SiteConfigManager,
};

// --- Componente Principal de la Página del Dashboard ---
export default function DashboardPage() {
  const { user, isLoading, isAuthenticated } = useAuth();
  const { activeView, setActiveView } = useDashboard();
  const router = useRouter();

  // Efecto para proteger la ruta y redirigir si no está autenticado
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  // Efecto para establecer la vista inicial basada en el rol del usuario
  useEffect(() => {
    if (user) {
      let defaultView: string;
      switch (user.role) {
        case 'PRESTADOR':
          defaultView = '/dashboard/prestadores';
          break;
        case 'ARTESANO':
          defaultView = '/dashboard/artesanos';
          break;
        case 'ADMIN':
        case 'FUNCIONARIO_DIRECTIVO':
        case 'FUNCIONARIO_PROFESIONAL':
          defaultView = '/dashboard/analytics'; // Vista principal para roles administrativos
          break;
        default:
          defaultView = 'inicio'; // Vista de bienvenida para cualquier otro caso
          break;
      }
      setActiveView(defaultView);
    }
  }, [user, setActiveView]);

  // Mostrar un estado de carga mientras se obtiene la información del usuario
  if (isLoading || !user) {
    return (
      <div className="flex items-center justify-center h-full p-4">
        <p className="text-lg text-gray-600">Cargando panel de control...</p>
      </div>
    );
  }

  // Renderizar el componente correspondiente a la vista activa
  const ActiveComponent = viewComponents[activeView] || WelcomeDashboard;

  return <ActiveComponent />;
}