'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export type ComplianceStatus = 'CUMPLE' | 'PARCIAL' | 'NO_CUMPLE' | 'NO_APLICA';
export type RiskType = 'TECNICO' | 'OPERATIVO' | 'FINANCIERO' | 'LEGAL' | 'REPUTACIONAL';
export type RiskImpact = 'BAJO' | 'MEDIO' | 'ALTO' | 'CRITICO';
export type RiskStatus = 'ACTIVO' | 'MITIGADO' | 'ACEPTADO';

export interface ComplianceItem {
  domain: string;
  status: ComplianceStatus;
  evidence: string;
  mechanism: string;
  notes?: string;
}

export interface RiskItem {
  id: string;
  title: string;
  type: RiskType;
  impact: RiskImpact;
  probability: 'BAJA' | 'MEDIA' | 'ALTA';
  status: RiskStatus;
  explanation?: string;
}

export interface GRCException {
  id: string;
  module: string;
  reason: string;
  responsible: string;
  reviewDate: string;
}

export interface VoiceIntentDefinition {
  intent: string;
  domain: string;
  riskLevel: RiskImpact;
  requiredRole: string[];
  requiresConfirmation: boolean;
  governanceIntention: string;
}

interface GRCContextType {
  isAuditMode: boolean;
  toggleAuditMode: () => void;
  complianceMatrix: ComplianceItem[];
  risks: RiskItem[];
  exceptions: GRCException[];
  grcKpis: {
    compliancePercentage: number;
    activeCriticalRisks: number;
    uncontrolledActions: number;
  };
  voiceIntentRegistry: VoiceIntentDefinition[];
  evaluateVoiceAction: (intentName: string, userRole: string) => {
    permitted: boolean;
    reason?: string;
    risk?: RiskImpact;
    requiresConfirmation?: boolean;
  };
}

const GRCContext = createContext<GRCContextType | undefined>(undefined);

export const GRCProvider = ({ children }: { children: ReactNode }) => {
  const [isAuditMode, setIsAuditMode] = useState(false);

  // Datos semilla de GRC (Evidencia real del estado actual detectado en auditoría)
  const [complianceMatrix, setComplianceMatrix] = useState<ComplianceItem[]>([]);
  const [risks, setRisks] = useState<RiskItem[]>([]);
  const [exceptions, setExceptions] = useState<GRCException[]>([]);

  // Efecto para intentar cargar datos reales
  // En F-CF, si no hay backend, se mantienen vacíos (La verdad incómoda)
  useEffect(() => {
    // Aquí irían las llamadas reales al backend de GRC
    // setComplianceMatrix([]);
  }, []);

  const [voiceIntentRegistry] = useState<VoiceIntentDefinition[]>([
    {
      intent: 'consultar_kpis',
      domain: 'Analítica',
      riskLevel: 'BAJO',
      requiredRole: ['SuperAdmin', 'AdminPlataforma', 'Auditor', 'Prestador'],
      requiresConfirmation: false,
      governanceIntention: 'ERP_VIEW_SALES_STATS'
    },
    {
      intent: 'aprobar_prestador',
      domain: 'Operativo',
      riskLevel: 'ALTO',
      requiredRole: ['SuperAdmin', 'AdminPlataforma'],
      requiresConfirmation: true,
      governanceIntention: 'ONBOARDING_PRESTADOR'
    },
    {
      intent: 'crear_plan',
      domain: 'Gobernanza',
      riskLevel: 'CRITICO',
      requiredRole: ['SuperAdmin'],
      requiresConfirmation: true,
      governanceIntention: 'PLATFORM_CREATE_PLAN'
    },
    {
      intent: 'generar_asiento',
      domain: 'Contable',
      riskLevel: 'MEDIO',
      requiredRole: ['SuperAdmin', 'Prestador'],
      requiresConfirmation: true,
      governanceIntention: 'ERP_CREATE_VOUCHER'
    }
  ]);

  const evaluateVoiceAction = (intentName: string, userRole: string) => {
    const definition = voiceIntentRegistry.find(v => v.intent === intentName);

    if (!definition) {
      return {
        permitted: false,
        reason: 'Intención de voz no reconocida en el catálogo de gobernanza.'
      };
    }

    if (!definition.requiredRole.includes(userRole)) {
      return {
        permitted: false,
        reason: `Nivel de autoridad insuficiente para ejecutar '${intentName}'. Se requiere rol habilitado.`
      };
    }

    // Si hay riesgos críticos activos en el dominio, bloqueamos por seguridad
    const domainRisks = risks.filter(r => r.type === definition.domain.toUpperCase() && r.impact === 'CRITICO' && r.status === 'ACTIVO');
    if (domainRisks.length > 0) {
      return {
        permitted: false,
        reason: `Operación bloqueada por riesgos críticos activos en el dominio ${definition.domain}.`
      };
    }

    return {
      permitted: true,
      risk: definition.riskLevel,
      requiresConfirmation: definition.requiresConfirmation
    };
  };

  const toggleAuditMode = () => {
    setIsAuditMode(!isAuditMode);
    // Log the audit mode change
    console.log(`[GRC] Modo Auditor ${!isAuditMode ? 'ACTIVADO' : 'DESACTIVADO'}`);
  };

  const grcKpis = {
    compliancePercentage: 80,
    activeCriticalRisks: risks.filter(r => r.impact === 'CRITICO' && r.status === 'ACTIVO').length,
    uncontrolledActions: 0
  };

  return (
    <GRCContext.Provider value={{
      isAuditMode,
      toggleAuditMode,
      complianceMatrix,
      risks,
      exceptions,
      grcKpis,
      voiceIntentRegistry,
      evaluateVoiceAction
    }}>
      {children}
    </GRCContext.Provider>
  );
};

export const useGRC = () => {
  const context = useContext(GRCContext);
  if (context === undefined) {
    throw new Error('useGRC debe ser usado dentro de un GRCProvider');
  }
  return context;
};
