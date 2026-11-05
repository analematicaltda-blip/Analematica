"use client";

import '../globals.css'; // Importación explícita de los estilos globales
import React, { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import Header from '@/components/Header';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter, usePathname } from 'next/navigation';
import { SADIVoiceLayer } from '@/ui/components/feedback/SADIVoiceLayer';
import { VoiceConfirmation } from '@/ui/components/feedback/VoiceConfirmation';
import { useSADI } from '@/hooks/useSADI';
import { useDashboard } from '@/contexts/DashboardContext';
import { FiEye, FiShield } from 'react-icons/fi';

// Componente interno para el layout autenticado
// Esto asegura que los hooks solo se usen dentro de un contexto autenticado y renderizado
const AuthenticatedLayout = ({ children, user }: { children: React.ReactNode, user: any }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const { isAuditMode } = useDashboard();
  const { state, responseMessage, processAudio, confirmationData, confirmAction, cancelAction } = useSADI();

  // Hook para bloquear el scroll del body cuando el sidebar móvil está abierto
  useEffect(() => {
    if (isSidebarOpen) {
      document.body.classList.add('overflow-hidden');
    } else {
      document.body.classList.remove('overflow-hidden');
    }
    // Limpieza al desmontar
    return () => {
      document.body.classList.remove('overflow-hidden');
    };
  }, [isSidebarOpen]);

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar para Desktop */}
      <div className="hidden lg:flex lg:flex-shrink-0">
        <Sidebar />
      </div>

      {/* Sidebar para Móvil (Drawer) */}
      <div
        className={`lg:hidden fixed inset-0 z-50 transition-transform transform ${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        role="dialog"
        aria-modal="true"
      >
        <div
          className="fixed inset-0 bg-black/60"
          aria-hidden="true"
          onClick={() => setIsSidebarOpen(false)}
        ></div>
        <div className="relative bg-white h-full w-64 shadow-xl">
          <Sidebar />
        </div>
      </div>

      <div className="flex flex-col flex-1 w-0 lg:overflow-x-hidden relative">
        {isAuditMode && (
          <div className="bg-amber-500 text-black px-4 py-1 text-[10px] font-black uppercase tracking-[0.3em] flex items-center justify-center gap-4 sticky top-0 z-[60] shadow-md">
            <FiEye size={14} />
            ESTADO INSTITUCIONAL: MODO AUDITORÍA ACTIVO ● TRAZABILIDAD FORZADA ● ACCIONES RESTRINGIDAS
            <FiEye size={14} />
          </div>
        )}
        {/* Placeholder para Modo Emergencia (Fase 5 Kill Switch) */}
        {user?.role === 'ADMIN' && typeof window !== 'undefined' && localStorage.getItem('emergency_mode') === 'true' && (
           <div className="bg-red-600 text-white px-4 py-2 text-xs font-black uppercase tracking-[0.4em] flex items-center justify-center gap-4 sticky top-0 z-[70] shadow-2xl animate-pulse">
              <FiShield size={16} />
              ALERTA SOBERANA: MODO EMERGENCIA ACTIVADO ● OPERACIONES BLOQUEADAS ● INVESTIGACIÓN EN CURSO
              <FiShield size={16} />
           </div>
        )}
        <Header isSidebarOpen={isSidebarOpen} setIsSidebarOpen={setIsSidebarOpen} />
        <main className="flex-1 relative z-0 focus:outline-none p-4 sm:p-6 lg:p-8">
          {children}
        </main>

        {/* Orquestador de Voz SADI */}
        <SADIVoiceLayer
          state={state}
          responseMessage={responseMessage}
          onAudioReady={processAudio}
        />

        <VoiceConfirmation
          isOpen={state === 'confirming'}
          message={confirmationData?.message || ""}
          onConfirm={confirmAction}
          onCancel={cancelAction}
        />
      </div>
    </div>
  );
};

const LoadingState = ({ isLoading }: { isLoading: boolean }) => {
  const [showError, setShowError] = useState(false);

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (isLoading) {
      timer = setTimeout(() => {
        setShowError(true);
      }, 8000); // 8 segundos para mostrar fallback de error
    }
    return () => clearTimeout(timer);
  }, [isLoading]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4 text-center">
      {!showError ? (
        <>
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-xl text-gray-600 font-medium">Verificando acceso...</p>
        </>
      ) : (
        <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full">
          <h2 className="text-2xl font-bold text-red-600 mb-4">La verificación está tardando más de lo esperado</h2>
          <p className="text-gray-600 mb-6">Es posible que haya un problema de conexión o sesión expirada.</p>
          <div className="flex flex-col gap-3">
            <button
              onClick={() => window.location.reload()}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Reintentar
            </button>
            <button
              onClick={() => {
                 localStorage.removeItem('authToken');
                 window.location.href = '/dashboard/login';
              }}
              className="text-blue-600 hover:underline"
            >
              Volver a iniciar sesión
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// Layout principal que maneja la lógica de enrutamiento y autenticación
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isLoading, isAuthenticated } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  // Mover todas las comprobaciones condicionales que retornan temprano al principio
  // sin llamar a hooks después de ellas.

  // Si estamos en páginas públicas, no se necesita el layout autenticado.
  if (pathname.startsWith('/dashboard/login') || pathname.startsWith('/dashboard/registro')) {
    return <>{children}</>;
  }

  if (isLoading) {
    return <LoadingState isLoading={isLoading} />;
  }

  if (!isAuthenticated && !pathname.startsWith('/dashboard/login') && !pathname.startsWith('/dashboard/registro')) {
    // Redirige al login si no está autenticado y no está ya en una página pública del dashboard
    router.push('/dashboard/login');
    return null; // O un componente de carga mientras redirige
  }

  if (user?.role === 'TURISTA') {
    router.push('/mi-viaje');
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <p className="text-xl text-gray-600">Acceso denegado. Redirigiendo...</p>
      </div>
    );
  }

  // Si todas las comprobaciones pasan, renderiza el layout autenticado.
  // Todos los hooks (useState, useEffect) están ahora dentro de este componente.
  return <AuthenticatedLayout user={user}>{children}</AuthenticatedLayout>;
}