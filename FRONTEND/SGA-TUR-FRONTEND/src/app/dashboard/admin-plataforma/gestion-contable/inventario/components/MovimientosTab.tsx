// frontend/src/app/dashboard/prestador/mi-negocio/gestion-contable/inventario/components/MovimientosTab.tsx
'use client';
import React, { useState, useCallback, useEffect } from 'react';
import { useMiNegocioApi } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import MovimientoInventarioForm from './MovimientoInventarioForm';
import { toast } from 'react-toastify';

export default function MovimientosTab() {
  const { getMovimientosInventario, createMovimientoInventario, isLoading } = useMiNegocioApi();
  const [movimientos, setMovimientos] = useState<any[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchMovimientos = useCallback(async () => {
    const data = await getMovimientosInventario();
    if (data && data.results) setMovimientos(data.results);
  }, [getMovimientosInventario]);

  useEffect(() => {
    fetchMovimientos();
  }, [fetchMovimientos]);

  const handleSubmit = async (values: any) => {
    const apiData = { ...values, producto: parseInt(values.producto) };
    const success = await createMovimientoInventario(apiData);
    if (success) {
      toast.success('Movimiento registrado');
      fetchMovimientos();
      setIsModalOpen(false);
    }
  };

  return (
    <>
      <div className="flex justify-end mb-4">
        <Button onClick={() => setIsModalOpen(true)}>Nuevo Movimiento</Button>
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Producto</TableHead>
            <TableHead>Tipo</TableHead>
            <TableHead>Cantidad</TableHead>
            <TableHead>Fecha</TableHead>
            <TableHead>Usuario</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {movimientos.map((m) => (
            <TableRow key={m.id}>
              <TableCell>{m.producto_nombre}</TableCell>
              <TableCell>{m.tipo_movimiento}</TableCell>
              <TableCell>{m.cantidad}</TableCell>
              <TableCell>{new Date(m.fecha).toLocaleString()}</TableCell>
              <TableCell>{m.usuario}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {isModalOpen && (
        <Modal title="Nuevo Movimiento de Inventario" isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
          <MovimientoInventarioForm
            onSubmit={handleSubmit}
            isSubmitting={isLoading}
          />
        </Modal>
      )}
    </>
  );
}
