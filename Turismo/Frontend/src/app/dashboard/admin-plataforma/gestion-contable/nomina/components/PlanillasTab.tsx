// frontend/src/app/dashboard/prestador/mi-negocio/gestion-contable/nomina/components/PlanillasTab.tsx
'use client';
import React, { useState, useCallback, useEffect } from 'react';
import { useMiNegocioApi, Planilla } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import PlanillaForm from './PlanillaForm';
import { toast } from 'react-toastify';

export default function PlanillasTab() {
  const { getPlanillas, createPlanilla, isLoading } = useMiNegocioApi();
  const [planillas, setPlanillas] = useState<Planilla[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchPlanillas = useCallback(async () => {
    const data = await getPlanillas();
    if (data && data.results) setPlanillas(data.results);
  }, [getPlanillas]);

  useEffect(() => {
    fetchPlanillas();
  }, [fetchPlanillas]);

  const handleSubmit = async (values: any) => {
    const success = await createPlanilla(values);
    if (success) {
      toast.success('Planilla liquidada');
      fetchPlanillas();
      setIsModalOpen(false);
    }
  };

  return (
    <>
      <div className="flex justify-end mb-4">
        <Button onClick={() => setIsModalOpen(true)}>Liquidar Planilla</Button>
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Periodo</TableHead>
            <TableHead>Neto a Pagar</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {planillas.map((p) => (
            <TableRow key={p.id}>
              <TableCell>{p.periodo_inicio} - {p.periodo_fin}</TableCell>
              <TableCell>${p.total_neto}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {isModalOpen && (
        <Modal title="Liquidar Nueva Planilla" isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
          <PlanillaForm
            onSubmit={handleSubmit}
            isSubmitting={isLoading}
          />
        </Modal>
      )}
    </>
  );
}
