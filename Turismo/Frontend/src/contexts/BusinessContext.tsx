'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

interface BusinessContextType {
  activeCompanyId: string | null;
  activePeriodId: string | null;
  setActiveCompanyId: (id: string | null) => void;
  setActivePeriodId: (id: string | null) => void;
}

const BusinessContext = createContext<BusinessContextType | undefined>(undefined);

export const BusinessProvider = ({ children }: { children: React.ReactNode }) => {
  const [activeCompanyId, setCompanyId] = useState<string | null>(null);
  const [activePeriodId, setPeriodId] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      setCompanyId(localStorage.getItem('activeCompanyId'));
      setPeriodId(localStorage.getItem('activePeriodId'));
    }
  }, []);

  const setActiveCompanyId = (id: string | null) => {
    setCompanyId(id);
    if (id) localStorage.setItem('activeCompanyId', id);
    else localStorage.removeItem('activeCompanyId');
  };

  const setActivePeriodId = (id: string | null) => {
    setPeriodId(id);
    if (id) localStorage.setItem('activePeriodId', id);
    else localStorage.removeItem('activePeriodId');
  };

  return (
    <BusinessContext.Provider value={{ activeCompanyId, activePeriodId, setActiveCompanyId, setActivePeriodId }}>
      {children}
    </BusinessContext.Provider>
  );
};

export const useBusiness = () => {
  const context = useContext(BusinessContext);
  if (context === undefined) {
    throw new Error('useBusiness must be used within a BusinessProvider');
  }
  return context;
};
