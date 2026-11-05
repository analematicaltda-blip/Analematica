'use client';

import React, { useState, useEffect } from 'react';
import api from '@/services/api';
import { toast } from 'react-toastify';
import { useForm, SubmitHandler } from 'react-hook-form';
import { FiArchive, FiPlus, FiEdit, FiTrash2, FiAlertTriangle } from 'react-icons/fi';
import { AuthGuard } from '@/components/ui/AuthGuard';
import Modal from '@/components/ui/Modal';

// --- Tipos ---
interface ItemInventario {
  id: number;
  nombre_item: string;
  descripcion: string;
  cantidad: number;
  unidad: string;
  punto_reorden: number;
}

type FormData = Omit<ItemInventario, 'id'>;

const InventarioManager = () => {
  const [items, setItems] = useState<ItemInventario[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<ItemInventario | null>(null);

  const { register, handleSubmit, reset, setValue } = useForm<FormData>();

  const fetchItems = async () => {
    setIsLoading(true);
    try {
      const response = await api.get('/empresa/inventario/');
      setItems(response.data.results || response.data);
    } catch (error) {
      toast.error('No se pudo cargar el inventario.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { fetchItems() }, []);

  const openModalForCreate = () => {
    reset();
    setEditingItem(null);
    setIsModalOpen(true);
  };

  const openModalForEdit = (item: ItemInventario) => {
    setEditingItem(item);
    setValue('nombre_item', item.nombre_item);
    setValue('descripcion', item.descripcion);
    setValue('cantidad', item.cantidad);
    setValue('unidad', item.unidad);
    setValue('punto_reorden', item.punto_reorden);
    setIsModalOpen(true);
  };

  const onSubmit: SubmitHandler<FormData> = async (data) => {
    const apiCall = editingItem
      ? api.patch(`/empresa/inventario/${editingItem.id}/`, data)
      : api.post('/empresa/inventario/', data);

    try {
      await apiCall;
      toast.success(`Ítem ${editingItem ? 'actualizado' : 'creado'} con éxito.`);
      fetchItems();
      setIsModalOpen(false);
    } catch (error) {
      toast.error('Error al guardar el ítem.');
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('¿Estás seguro de que deseas eliminar este ítem del inventario?')) {
        try {
            await api.delete(`/empresa/inventario/${id}/`);
            toast.success('Ítem eliminado.');
            fetchItems();
        } catch (error) {
            toast.error('No se pudo eliminar el ítem.');
        }
    }
  }

  if (isLoading) return <div>Cargando inventario...</div>;

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Gestionar Inventario</h1>
        <button onClick={openModalForCreate} className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
          <FiPlus className="mr-2" />
          Añadir Ítem
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full bg-white">
          <thead className="bg-gray-50">
            <tr>
              <th className="py-3 px-4 text-left">Nombre</th>
              <th className="py-3 px-4 text-left">Cantidad</th>
              <th className="py-3 px-4 text-left">Punto de Reorden</th>
              <th className="py-3 px-4 text-left">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {items.map(item => (
              <tr key={item.id} className="border-b">
                <td className="py-3 px-4 font-medium">{item.nombre_item}</td>
                <td className={`py-3 px-4 ${item.cantidad <= item.punto_reorden ? 'text-red-500 font-bold' : ''}`}>
                    {item.cantidad <= item.punto_reorden && <FiAlertTriangle className="inline mr-2" />}
                    {item.cantidad} {item.unidad}
                </td>
                <td className="py-3 px-4">{item.punto_reorden} {item.unidad}</td>
                <td className="py-3 px-4">
                  <button onClick={() => openModalForEdit(item)} className="p-2 text-gray-500 hover:text-blue-600"><FiEdit /></button>
                  <button onClick={() => handleDelete(item.id)} className="p-2 text-gray-500 hover:text-red-600"><FiTrash2 /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {items.length === 0 && <p className="text-center py-8">No hay ítems en el inventario.</p>}
      </div>

      {isModalOpen && (
        <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title={editingItem ? "Editar Ítem" : "Crear Nuevo Ítem"}>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <input {...register('nombre_item', { required: true })} placeholder="Nombre del Ítem" className="w-full p-2 border rounded"/>
                <textarea {...register('descripcion')} placeholder="Descripción" rows={3} className="w-full p-2 border rounded"/>
                <input {...register('unidad', { required: true })} placeholder="Unidad (ej: kg, uds, litros)" className="w-full p-2 border rounded"/>
                <input type="number" {...register('cantidad', { required: true, valueAsNumber: true })} placeholder="Cantidad Actual" className="w-full p-2 border rounded"/>
                <input type="number" {...register('punto_reorden', { required: true, valueAsNumber: true })} placeholder="Punto de Reorden" className="w-full p-2 border rounded"/>
                <button type="submit" className="w-full px-4 py-2 bg-blue-600 text-white rounded-md">Guardar</button>
            </form>
        </Modal>
      )}
    </div>
  );
};

const InventarioPage = () => <AuthGuard allowedRoles={['PRESTADOR']}><InventarioManager /></AuthGuard>;
export default InventarioPage;