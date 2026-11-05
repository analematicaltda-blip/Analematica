// frontend/src/app/dashboard/prestador/mi-negocio/gestion-contable/compras/components/ProveedoresTab.tsx
'use client';
import React, { useState, useCallback, useEffect } from 'react';
import { useMiNegocioApi } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import ProveedorForm from './ProveedorForm';
import { toast } from 'react-toastify';
import { Input } from '@/components/ui/Input';

// Definimos el tipo aquí para usarlo localmente
export interface Proveedor {
  id: number;
  nombre: string;
  identificacion?: string;
  telefono?: string;
  email?: string;
  direccion?: string;
}

export default function ProveedoresTab() {
  const { getProveedores, createProveedor, updateProveedor, deleteProveedor, isLoading } = useMiNegocioApi();
  const [proveedores, setProveedores] = useState<Proveedor[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedProveedor, setSelectedProveedor] = useState<Proveedor | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredProveedores = proveedores.filter(p =>
    p.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.identificacion?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const fetchProveedores = useCallback(async () => {
    const data = await getProveedores();
    if (data && data.results) {
      setProveedores(data.results);
    }
  }, [getProveedores]);

  useEffect(() => {
    fetchProveedores();
  }, [fetchProveedores]);

  const handleOpenModal = (proveedor: Proveedor | null = null) => {
    setSelectedProveedor(proveedor);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setSelectedProveedor(null);
    setIsModalOpen(false);
  };

  const handleSubmit = async (values: any) => {
    let success;
    if (selectedProveedor) {
      success = await updateProveedor(selectedProveedor.id, values);
    } else {
      success = await createProveedor(values);
    }

    if (success) {
      toast.success(selectedProveedor ? 'Proveedor actualizado' : 'Proveedor creado');
      fetchProveedores();
      handleCloseModal();
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('¿Seguro que quieres eliminar este proveedor?')) {
      const success = await deleteProveedor(id);
      if (success) {
        toast.success('Proveedor eliminado');
        fetchProveedores();
      }
    }
  };

  return (
    <>
      <div className="flex justify-between items-center mb-4">
        <Input
          placeholder="Buscar por nombre o identificación..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="max-w-sm"
        />
        <Button onClick={() => handleOpenModal()}>Nuevo Proveedor</Button>
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Nombre</TableHead>
            <TableHead>Identificación</TableHead>
            <TableHead>Teléfono</TableHead>
            <TableHead>Email</TableHead>
            <TableHead>Acciones</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filteredProveedores.map((p) => (
            <TableRow key={p.id}>
              <TableCell>{p.nombre}</TableCell>
              <TableCell>{p.identificacion}</TableCell>
              <TableCell>{p.telefono}</TableCell>
              <TableCell>{p.email}</TableCell>
              <TableCell>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" onClick={() => handleOpenModal(p)}>Editar</Button>
                  <Button variant="destructive" size="sm" onClick={() => handleDelete(p.id)}>Eliminar</Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {isModalOpen && (
        <Modal title={selectedProveedor ? 'Editar Proveedor' : 'Nuevo Proveedor'} isOpen={isModalOpen} onClose={handleCloseModal}>
          <ProveedorForm
            onSubmit={handleSubmit}
            initialData={selectedProveedor || undefined}
            isSubmitting={isLoading}
          />
        </Modal>
      )}
    </>
  );
}
