'use client';

import React, { useState, useEffect, useCallback } from 'react';
import api from '@/services/api';
import { useForm, SubmitHandler } from 'react-hook-form';
import Modal from '@/components/shared/Modal';
import { toast } from 'react-toastify';

interface Recurso {
  id: number;
  nombre: string;
  tipo_recurso: 'HUMANO' | 'LOGISTICO' | 'TECNOLOGICO';
  disponible: boolean;
}

type FormInputs = Omit<Recurso, 'id'>;

const Recursos = () => {
  const [recursos, setRecursos] = useState<Recurso[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRecurso, setEditingRecurso] = useState<Recurso | null>(null);

  const { register, handleSubmit, reset, setValue } = useForm<FormInputs>();

  const fetchRecursos = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await api.get('/empresa/recursos/');
      setRecursos(response.data.results || []);
    } catch (err: any) {
      setError('No se pudieron cargar los recursos. ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRecursos();
  }, [fetchRecursos]);

  const openModalForCreate = () => {
    reset({ nombre: '', tipo_recurso: 'HUMANO', disponible: true });
    setEditingRecurso(null);
    setIsModalOpen(true);
  };

  const openModalForEdit = (recurso: Recurso) => {
    setEditingRecurso(recurso);
    setValue('nombre', recurso.nombre);
    setValue('tipo_recurso', recurso.tipo_recurso);
    setValue('disponible', recurso.disponible);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingRecurso(null);
    reset();
  };

  const onSubmit: SubmitHandler<FormInputs> = async (data) => {
    try {
      if (editingRecurso) {
        await api.patch(`/empresa/recursos/${editingRecurso.id}/`, data);
        toast.success('Recurso actualizado con éxito');
      } else {
        await api.post('/empresa/recursos/', data);
        toast.success('Recurso creado con éxito');
      }
      closeModal();
      fetchRecursos();
    } catch (err: any) {
      toast.error('Error al guardar el recurso: ' + (err.response?.data?.detail || err.message));
    }
  };

  if (isLoading) return <div>Cargando recursos...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Gestión de Recursos</h1>
        <button onClick={openModalForCreate} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
          Añadir Recurso
        </button>
      </div>

      <Modal isOpen={isModalOpen} onClose={closeModal} title={editingRecurso ? 'Editar Recurso' : 'Nuevo Recurso'}>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label htmlFor="nombre" className="block text-sm font-medium text-gray-700">Nombre del Recurso</label>
            <input id="nombre" {...register('nombre', { required: true })} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm" />
          </div>
          <div>
            <label htmlFor="tipo_recurso" className="block text-sm font-medium text-gray-700">Tipo de Recurso</label>
            <select id="tipo_recurso" {...register('tipo_recurso')} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
              <option value="HUMANO">Humano</option>
              <option value="LOGISTICO">Logístico</option>
              <option value="TECNOLOGICO">Tecnológico</option>
            </select>
          </div>
          <div className="flex items-center">
            <input id="disponible" type="checkbox" {...register('disponible')} className="h-4 w-4 text-blue-600 border-gray-300 rounded" />
            <label htmlFor="disponible" className="ml-2 block text-sm text-gray-900">Disponible</label>
          </div>
          <div className="flex justify-end space-x-2">
            <button type="button" onClick={closeModal} className="px-4 py-2 bg-gray-200 rounded">Cancelar</button>
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">Guardar</button>
          </div>
        </form>
      </Modal>

      {recursos.length === 0 ? (
        <p>No tienes recursos registrados.</p>
      ) : (
        <table className="min-w-full bg-white">
          <thead>
            <tr>
              <th className="py-2 px-4 border-b text-left">Nombre</th>
              <th className="py-2 px-4 border-b text-left">Tipo</th>
              <th className="py-2 px-4 border-b text-left">Disponible</th>
              <th className="py-2 px-4 border-b text-left">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {recursos.map((recurso) => (
              <tr key={recurso.id}>
                <td className="py-2 px-4 border-b">{recurso.nombre}</td>
                <td className="py-2 px-4 border-b">{recurso.tipo_recurso}</td>
                <td className="py-2 px-4 border-b">{recurso.disponible ? 'Sí' : 'No'}</td>
                <td className="py-2 px-4 border-b">
                  <button onClick={() => openModalForEdit(recurso)} className="text-blue-500 hover:underline">Editar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default Recursos;