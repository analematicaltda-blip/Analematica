// frontend/src/app/dashboard/prestador/mi-negocio/gestion-contable/informes/components/LibroMayorTab.tsx
'use client';
import React, { useState, useEffect } from 'react';
import { useMiNegocioApi, ChartOfAccount } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';

export default function LibroMayorTab() {
  const { getLibroMayor, getChartOfAccounts, isLoading } = useMiNegocioApi();
  const [cuentas, setCuentas] = useState<ChartOfAccount[]>([]);
  const [filtros, setFiltros] = useState({ cuenta: '', inicio: '', fin: '' });
  const [resultado, setResultado] = useState<any[]>([]);

  useEffect(() => {
    async function loadCuentas() {
      const data = await getChartOfAccounts();
      if(data && data.results) setCuentas(data.results);
    }
    loadCuentas();
  }, [getChartOfAccounts]);

  const handleGenerate = async () => {
    const data = await getLibroMayor({
      codigo_cuenta: filtros.cuenta,
      fecha_inicio: filtros.inicio,
      fecha_fin: filtros.fin
    });
    if(data) setResultado(data);
  };

  return (
    <div className="space-y-4">
      <div className="flex space-x-2 items-end">
        {/* Filtros */}
        <Button onClick={handleGenerate} disabled={isLoading}>Generar</Button>
      </div>
      <Table>{/* ... tabla de resultados ... */}</Table>
    </div>
  );
}
