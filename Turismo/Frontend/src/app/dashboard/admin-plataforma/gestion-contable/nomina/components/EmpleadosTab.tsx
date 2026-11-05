// frontend/src/app/dashboard/prestador/mi-negocio/gestion-contable/nomina/components/EmpleadosTab.tsx
'use client';
import React, { useState, useCallback, useEffect } from 'react';
import { useMiNegocioApi, Empleado } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import EmpleadoForm from './EmpleadoForm';
import { toast } from 'react-toastify';

export default function EmpleadosTab() {
  const { getEmpleados, createEmpleado, updateEmpleado, deleteEmpleado, isLoading } = useMiNegocioApi();
  const [empleados, setEmpleados] = useState<Empleado[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedEmpleado, setSelectedEmpleado] = useState<Empleado | null>(null);

  const fetchEmpleados = useCallback(async () => {
    const data = await getEmpleados();
    if (data && data.results) setEmpleados(data.results);
  }, [getEmpleados]);

  useEffect(() => {
    fetchEmpleados();
  }, [fetchEmpleados]);

  const handleOpenModal = (empleado: Empleado | null = null) => {
    setSelectedEmpleado(empleado);
    setIsModalOpen(true);
  };

  const handleSubmit = async (values: any) => {
    let success;
    if (selectedEmpleado) {
      success = await updateEmpleado(selectedEmpleado.id, values);
    } else {
      success = await createEmpleado(values);
    }
    if (success) {
      fetchEmpleados();
      setIsModalOpen(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('¿Seguro que quieres eliminar este empleado?')) {
      const success = await deleteEmpleado(id);
      if (success) {
        toast.success('Empleado eliminado');
        fetchEmpleados();
      }
    }
  };

  return (
    <>
      <div className="flex justify-end mb-4">
        <Button onClick={() => handleOpenModal()}>Nuevo Empleado</Button>
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Nombre</TableHead>
            <TableHead>Identificación</TableHead>
            <TableHead>Email</TableHead>
            <TableHead>Acciones</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {empleados.map((e) => (
            <TableRow key={e.id}>
              <TableCell>{e.nombre} {e.apellido}</TableCell>
              <TableCell>{e.identificacion}</TableCell>
              <TableCell>{e.email}</TableCell>
              <TableCell>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" onClick={() => handleOpenModal(e)}>Editar</Button>
                  <Button variant="destructive" size="sm" onClick={() => handleDelete(e.id)}>Eliminar</Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {isModalOpen && (
        <Modal title={selectedEmpleado ? 'Editar Empleado' : 'Nuevo Empleado'} isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
          <EmpleadoForm
            onSubmit={handleSubmit}
            initialData={selectedEmpleado || undefined}
            isSubmitting={isLoading}
          />
        </Modal>
      )}
    </>
  );
}
