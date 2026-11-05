import React, { createContext, useContext, useState, useEffect } from 'react';
import { auditLogger } from '@/services/auditLogger';

interface DashboardContextType {
  isAuditMode: boolean;
  setAuditMode: (enabled: boolean) => void;
  toggleAuditMode: () => void;
}

const DashboardContext = createContext<DashboardContextType | undefined>(undefined);

export const useDashboard = () => {
  const context = useContext(DashboardContext);
  if (context === undefined) {
    throw new Error('useDashboard must be used within a DashboardProvider');
  }
  return context;
};

export const DashboardProvider = ({ children }: { children: React.ReactNode }) => {
  const [isAuditMode, setIsAuditMode] = useState(false);

  const setAuditMode = (enabled: boolean) => {
    setIsAuditMode(enabled);
    auditLogger.log({
        type: 'ACTION_PERMITTED',
        view: 'Global',
        action: `Audit Mode ${enabled ? 'Enabled' : 'Disabled'}`,
        userRole: 'ADMIN', // This should be dynamic but context doesn't have auth yet
        status: 'INFO'
    });
  };

  const toggleAuditMode = () => setAuditMode(!isAuditMode);

  const value = {
    isAuditMode,
    setAuditMode,
    toggleAuditMode
  };

  return <DashboardContext.Provider value={value}>{children}</DashboardContext.Provider>;
};

export default DashboardContext;
