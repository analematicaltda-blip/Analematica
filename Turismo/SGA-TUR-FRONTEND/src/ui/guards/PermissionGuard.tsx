'use client';

import React, { ReactNode } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useDashboard } from '@/contexts/DashboardContext';

export type AppRole =
  | 'SuperAdmin'
  | 'AdminPlataforma'
  | 'Auditor'
  | 'OperadorComercial'
  | 'OperadorFinanciero'
  | 'Prestador'
  | 'Artesano'
  | 'Turista'
  | 'Observador';

interface PermissionGuardProps {
  children: ReactNode;
  allowedRoles?: AppRole[];
  deniedRoles?: AppRole[];
  fallback?: ReactNode;
  requireSuperuser?: boolean;
}

/**
 * Mapeo de roles de backend a roles interpretados de negocio (F-C+)
 */
export const mapBackendRoleToAppRole = (user: any): AppRole => {
  if (!user) return 'Observador';

  if (user.is_superuser && user.role === 'ADMIN') return 'SuperAdmin';

  switch (user.role) {
    case 'ADMIN':
    case 'ADMIN_ENTIDAD':
    case 'ADMIN_DEPARTAMENTAL':
    case 'ADMIN_MUNICIPAL':
      return 'AdminPlataforma';
    case 'FUNCIONARIO_DIRECTIVO':
      return 'Auditor';
    case 'FUNCIONARIO_PROFESIONAL':
      // Aquí se podría discriminar por departamento/área si existiera el dato,
      // por ahora mapeamos a Operador genérico que luego se especializa.
      return 'OperadorComercial';
    case 'PRESTADOR':
      return 'Prestador';
    case 'ARTESANO':
      return 'Artesano';
    case 'TURISTA':
      return 'Turista';
    case 'CONSEJO_CONSULTIVO_TURISMO':
      return 'Auditor';
    default:
      return 'Observador';
  }
};

export const usePermissions = () => {
  const { user } = useAuth();
  const { isAuditMode } = useDashboard();
  const appRole = mapBackendRoleToAppRole(user);

  const hasPermission = (allowedRoles: AppRole[]) => {
    if (isAuditMode) return false; // En modo auditor no se permiten acciones restringidas
    return allowedRoles.includes(appRole);
  };

  const isReadOnly = isAuditMode || appRole === 'Auditor' || appRole === 'Observador';

  return {
    role: appRole,
    user,
    hasPermission,
    isReadOnly,
    isSuperAdmin: appRole === 'SuperAdmin'
  };
};

export const PermissionGuard: React.FC<PermissionGuardProps> = ({
  children,
  allowedRoles,
  deniedRoles,
  fallback = null,
  requireSuperuser = false
}) => {
  const { role, user } = usePermissions();

  if (requireSuperuser && role !== 'SuperAdmin') return <>{fallback}</>;

  if (allowedRoles && !allowedRoles.includes(role)) return <>{fallback}</>;

  if (deniedRoles && deniedRoles.includes(role)) return <>{fallback}</>;

  return <>{children}</>;
};
