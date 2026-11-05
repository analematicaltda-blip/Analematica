'use client';

import React, { useState, useEffect, useCallback } from 'react';
import api from '@/services/api';
import { useForm, SubmitHandler } from 'react-hook-form';
import Modal from '@/components/shared/Modal';
import { toast } from 'react-toastify';

interface InventarioItem {
  id: number;
  nombre_item: string;
  descripcion: string;
  cantidad: number;
  unidad: string;
  punto_reorden: number;
}

type FormInputs = Omit<InventarioItem, 'id'>;

const Inventario = () => {
  const [items, setItems] = useState<InventarioItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<InventarioItem | null>(null);

  const { register, handleSubmit, reset, setValue } = useForm<FormInputs>();

  const fetchInventario = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await api.get('/empresa/inventario/');
      setItems(response.data.results || []);
    } catch (err: any) {
      setError('No se pudo cargar el inventario. ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInventario();
  }, [fetchInventario]);

  const openModalForCreate = () => {
    reset({ nombre_item: '', descripcion: '', cantidad: 0, unidad: '', punto_reorden: 0 });
    setEditingItem(null);
    setIsModalOpen(true);
  };

  const openModalForEdit = (item: InventarioItem) => {
    setEditingItem(item);
    setValue('nombre_item', item.nombre_item);
    setValue('descripcion', item.descripcion);
    setValue('cantidad', item.cantidad);
    setValue('unidad', item.unidad);
    setValue('punto_reorden', item.punto_reorden);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingItem(null);
    reset();
  };

  const onSubmit: SubmitHandler<FormInputs> = async (data) => {
    try {
      if (editingItem) {
        await api.patch(`/empresa/inventario/${editingItem.id}/`, data);
        toast.success('Ítem de inventario actualizado con éxito');
      } else {
        await api.post('/empresa/inventario/', data);
        toast.success('Ítem de inventario creado con éxito');
      }
      closeModal();
      fetchInventario();
    } catch (err: any) {
      toast.error('Error al guardar el ítem: ' + (err.response?.data?.detail || err.message));
    }
  };

  if (isLoading) return <div>Cargando inventario...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Gestión de Inventario</h1>
        <button onClick={openModalForCreate} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
          Añadir Ítem
        </button>
      </div>

      <Modal isOpen={isModalOpen} onClose={closeModal} title={editingItem ? 'Editar Ítem' : 'Nuevo Ítem'}>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label htmlFor="nombre_item" className="block text-sm font-medium text-gray-700">Nombre del Ítem</label>
            <input id="nombre_item" {...register('nombre_item', { required: true })} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm" />
          </div>
           <div>
            <label htmlFor="descripcion" className="block text-sm font-medium text-gray-700">Descripción</label>
            <textarea id="descripcion" {...register('descripcion')} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm" />
          </div>
          <div>
            <label htmlFor="cantidad" className="block text-sm font-medium text-gray-700">Cantidad</label>
            <input id="cantidad" type="number" {...register('cantidad', { required: true, valueAsNumber: true, min: 0 })} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm" />
          </div>
           <div>
            <label htmlFor="unidad" className="block text-sm font-medium text-gray-700">Unidad (ej: kg, litros, uds.)</label>
            <input id="unidad" {...register('unidad', { required: true })} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm" />
          </div>
          <div>
            <label htmlFor="punto_reorden" className="block text-sm font-medium text-gray-700">Punto de Reorden</label>
            <input id="punto_reorden" type="number" {...register('punto_reorden', { required: true, valueAsNumber: true, min: 0 })} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm" />
          </div>
          <div className="flex justify-end space-x-2">
            <button type="button" onClick={closeModal} className="px-4 py-2 bg-gray-200 rounded">Cancelar</button>
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">Guardar</button>
          </div>
        </form>
      </Modal>

      {items.length === 0 ? (
        <p>No tienes ítems en tu inventario.</p>
      ) : (
        <table className="min-w-full bg-white">
          <thead>
            <tr>
              <th className="py-2 px-4 border-b text-left">Ítem</th>
              <th className="py-2 px-4 border-b text-left">Cantidad</th>
              <th className="py-2 px-4 border-b text-left">Punto de Reorden</th>
              <th className="py-2 px-4 border-b text-left">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td className="py-2 px-4 border-b">{item.nombre_item}</td>
                <td className="py-2 px-4 border-b">{item.cantidad} {item.unidad}</td>
                <td className="py-2 px-4 border-b">{item.punto_reorden}</td>
                <td className="py-2 px-4 border-b">
                  <button onClick={() => openModalForEdit(item)} className="text-blue-500 hover:underline">Editar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default Inventario;