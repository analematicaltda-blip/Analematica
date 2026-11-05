'use client';

import { useEntity, Entity } from '@/contexts/EntityContext';
import { useAuth } from '@/contexts/AuthContext';
import { useCallback } from 'react';

/**
 * Hook unificado para acceder al contexto del Tenant/Empresa activa.
 * Cumple con la Fase 2: Normalización de Identidades y Contexto Operativo.
 */
export const useTenant = () => {
  const { entity, isLoading: isEntityLoading, switchEntity, clearEntity } = useEntity();
  const { user, isLoading: isAuthLoading } = useAuth();

  const isReady = !isEntityLoading && !isAuthLoading && (!!entity || !user);

  const getTenantId = useCallback(() => {
    return entity?.id || null;
  }, [entity]);

  return {
    tenant: entity,
    tenantId: getTenantId(),
    isLoading: isEntityLoading || isAuthLoading,
    isReady,
    switchTenant: switchEntity,
    clearTenant: clearEntity,
    // Helpers adicionales
    isSovereign: user?.role === 'ADMIN',
    contextName: entity?.name || 'Contexto Global',
  };
};
