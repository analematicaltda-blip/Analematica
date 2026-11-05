// frontend/src/app/dashboard/prestador/mi-negocio/gestion-contable/informes/components/BalanceComprobacionTab.tsx
'use client';
import React, { useState } from 'react';
import { useMiNegocioApi } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';

export default function BalanceComprobacionTab() {
  const { getBalanceComprobacion, isLoading } = useMiNegocioApi();
  const [fecha, setFecha] = useState('');
  const [resultado, setResultado] = useState<any>(null);

  const handleGenerate = async () => {
    const data = await getBalanceComprobacion({ fecha_fin: fecha });
    if(data) setResultado(data);
  };

  return (
    <div className="space-y-4">
      <div className="flex space-x-2 items-end">
        <Input type="date" value={fecha} onChange={e => setFecha(e.target.value)} />
        <Button onClick={handleGenerate} disabled={isLoading}>Generar</Button>
      </div>
      {resultado && <Table>{/* ... tabla ... */}</Table>}
    </div>
  );
}
