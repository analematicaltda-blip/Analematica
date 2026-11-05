// src/app/dashboard/admin-plataforma/hooks/useMiNegocioApi.ts
import { useState, useCallback } from 'react';
import api from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'react-toastify';

// --- Tipos de Datos Genéricos---
interface PerfilData {
  nombre_comercial: string;
  telefono_principal: string;
  email_comercial: string;
  direccion: string;
  descripcion_corta: string;
}

export interface Cliente {
  id: number;
  nombre: string;
  email: string;
  telefono: string | null;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Proveedor {
  id: number;
  nombre: string;
  identificacion: string | null;
  telefono: string | null;
  email: string | null;
  direccion: string | null;
}

export interface Producto {
  id: number;
  nombre: string;
  sku: string;
  categoria: number;
  categoria_nombre?: string;
  descripcion: string;
  costo: string;
  precio_venta: string;
  stock_actual: string;
  stock_minimo: string;
}

export interface ChartOfAccount {
  code: string;
  name: string;
  nature: 'DEBITO' | 'CREDITO';
  allows_transactions: boolean;
}

export interface JournalEntry {
  id: number;
  perfil: number;
  entry_date: string;
  description: string;
  entry_type: string;
  user: number;
  created_at: string;
}

export interface BankAccount {
  id: number;
  bank_name: string;
  account_number: string;
  account_holder: string;
  account_type: 'SAVINGS' | 'CHECKING';
  balance: string;
}

export interface CashTransaction {
  id: number;
  cuenta: number;
  fecha: string;
  tipo: 'INGRESO' | 'EGRESO' | 'TRANSFERENCIA';
  monto: string;
  descripcion: string;
}

export function useMiNegocioApi() {
  const { token } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const makeRequest = useCallback(async <T>(requestFunc: () => Promise<T>, successMessage?: string): Promise<T | null> => {
    if (!token) { setError("No autenticado."); return null; }
    setIsLoading(true); setError(null);
    try {
      const result = await requestFunc();
      if (successMessage) toast.success(successMessage);
      return result;
    } catch (err: any) {
      const msg = err.response?.data?.detail || "Ocurrió un error.";
      setError(msg); toast.error(msg);
      return null;
    } finally { setIsLoading(false); }
  }, [token]);

  // --- API de Perfil ---
  const getPerfil = useCallback(async () => {
    return makeRequest(() => api.get<PerfilData>('/admin/plataforma/operativa/perfil/').then(res => res.data));
  }, [makeRequest]);

  // --- API de Clientes ---
  const getClientes = useCallback(async () => {
    return makeRequest(() => api.get<PaginatedResponse<Cliente>>('/admin/plataforma/operativa/clientes/').then(res => res.data));
  }, [makeRequest]);

  // --- API de Contabilidad ---
  const getChartOfAccounts = useCallback(async () => {
    return makeRequest(() => api.get<ChartOfAccount[]>('/admin/plataforma/contable/plan-cuentas/').then(res => res.data));
  }, [makeRequest]);

  const getJournalEntries = useCallback(async () => {
    return makeRequest(() => api.get<JournalEntry[]>('/admin/plataforma/contable/asientos/').then(res => res.data));
  }, [makeRequest]);

  // --- API Financiera ---
  const getBankAccounts = useCallback(async () => {
    return makeRequest(() => api.get<BankAccount[]>('/admin/plataforma/financiera/cuentas/').then(res => res.data));
  }, [makeRequest]);

  const getCashTransactions = useCallback(async () => {
    return makeRequest(() => api.get<CashTransaction[]>('/admin/plataforma/financiera/transacciones/').then(res => res.data));
  }, [makeRequest]);

  // --- API de Gestión Archivística ---
  const getArchivisticaDocumentos = useCallback(async () => {
    return makeRequest(() => api.get<any[]>('/admin/plataforma/archivistica/documentos/').then(res => res.data));
  }, [makeRequest]);

  return {
    isLoading,
    error,
    getPerfil,
    getClientes,
    getChartOfAccounts,
    getJournalEntries,
    getBankAccounts,
    getCashTransactions,
    getArchivisticaDocumentos,
  };
}
