// frontend/src/app/dashboard/prestador/mi-negocio/gestion-contable/nomina/components/EmpleadosTab.tsx
'use client';
import React, { useState, useCallback, useEffect } from 'react';
import { useMiNegocioApi, Empleado } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import EmpleadoForm from './EmpleadoForm';
import { toast } from 'react-toastify';
import { CriticalActionDialog } from '@/components/ui/CriticalActionDialog';

export default function EmpleadosTab() {
  const { getEmpleados, createEmpleado, updateEmpleado, deleteEmpleado, isLoading } = useMiNegocioApi();
  const [empleados, setEmpleados] = useState<Empleado[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedEmpleado, setSelectedEmpleado] = useState<Empleado | null>(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [empleadoToDelete, setEmpleadoToDelete] = useState<number | null>(null);

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

  const handleDeleteRequest = (id: number) => {
    setEmpleadoToDelete(id);
    setIsDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (empleadoToDelete) {
      const success = await deleteEmpleado(empleadoToDelete);
      if (success) {
        toast.success('Registro de empleado eliminado del sistema.');
        fetchEmpleados();
      }
      setIsDeleteDialogOpen(false);
      setEmpleadoToDelete(null);
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
                  <Button variant="destructive" size="sm" onClick={() => handleDeleteRequest(e.id)}>Eliminar</Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <CriticalActionDialog
        isOpen={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
        onConfirm={handleConfirmDelete}
        title="¿Eliminar Empleado?"
        description="Esta acción desvinculará al empleado de los procesos operativos actuales. El historial contable permanecerá intacto por ley."
        confirmLabel="Eliminar Definitivamente"
        type="danger"
        isLoading={isLoading}
      />

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
