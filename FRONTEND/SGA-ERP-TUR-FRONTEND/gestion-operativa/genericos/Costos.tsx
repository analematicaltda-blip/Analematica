'use client';

import React, { useState, useEffect, useCallback } from 'react';
import api from '@/services/api';
import { useForm, SubmitHandler } from 'react-hook-form';
import Modal from '@/components/shared/Modal';
import { toast } from 'react-toastify';

interface Costo {
  id: number;
  concepto: string;
  monto: string;
  fecha: string;
  tipo_costo: 'FIJO' | 'VARIABLE';
  es_recurrente: boolean;
}

type FormInputs = Omit<Costo, 'id'>;

const Costos = () => {
  const [costos, setCostos] = useState<Costo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCosto, setEditingCosto] = useState<Costo | null>(null);

  const { register, handleSubmit, reset, setValue } = useForm<FormInputs>();

  const fetchCostos = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await api.get('/empresa/costos/');
      setCostos(response.data.results || []);
    } catch (err: any) {
      setError('No se pudieron cargar los costos. ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCostos();
  }, [fetchCostos]);

  const openModalForCreate = () => {
    reset({ concepto: '', monto: '0.00', fecha: new Date().toISOString().split('T')[0], tipo_costo: 'VARIABLE', es_recurrente: false });
    setEditingCosto(null);
    setIsModalOpen(true);
  };

  const openModalForEdit = (costo: Costo) => {
    setEditingCosto(costo);
    setValue('concepto', costo.concepto);
    setValue('monto', costo.monto);
    setValue('fecha', costo.fecha);
    setValue('tipo_costo', costo.tipo_costo);
    setValue('es_recurrente', costo.es_recurrente);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingCosto(null);
    reset();
  };

  const onSubmit: SubmitHandler<FormInputs> = async (data) => {
    try {
      if (editingCosto) {
        await api.patch(`/empresa/costos/${editingCosto.id}/`, data);
        toast.success('Costo actualizado con éxito');
      } else {
        await api.post('/empresa/costos/', data);
        toast.success('Costo creado con éxito');
      }
      closeModal();
      fetchCostos();
    } catch (err: any) {
      toast.error('Error al guardar el costo: ' + (err.response?.data?.detail || err.message));
    }
  };

  if (isLoading) return <div>Cargando costos...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Gestión de Costos</h1>
        <button onClick={openModalForCreate} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
          Añadir Costo
        </button>
      </div>

      <Modal isOpen={isModalOpen} onClose={closeModal} title={editingCosto ? 'Editar Costo' : 'Nuevo Costo'}>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label htmlFor="concepto" className="block text-sm font-medium text-gray-700">Concepto</label>
            <input id="concepto" {...register('concepto', { required: true })} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm" />
          </div>
          <div>
            <label htmlFor="monto" className="block text-sm font-medium text-gray-700">Monto</label>
            <input id="monto" type="number" step="0.01" {...register('monto', { required: true, valueAsNumber: true })} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm" />
          </div>
          <div>
            <label htmlFor="fecha" className="block text-sm font-medium text-gray-700">Fecha</label>
            <input id="fecha" type="date" {...register('fecha', { required: true })} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm" />
          </div>
          <div>
            <label htmlFor="tipo_costo" className="block text-sm font-medium text-gray-700">Tipo de Costo</label>
            <select id="tipo_costo" {...register('tipo_costo')} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
              <option value="VARIABLE">Variable</option>
              <option value="FIJO">Fijo</option>
            </select>
          </div>
          <div className="flex items-center">
            <input id="es_recurrente" type="checkbox" {...register('es_recurrente')} className="h-4 w-4 text-blue-600 border-gray-300 rounded" />
            <label htmlFor="es_recurrente" className="ml-2 block text-sm text-gray-900">Es Recurrente</label>
          </div>
          <div className="flex justify-end space-x-2">
            <button type="button" onClick={closeModal} className="px-4 py-2 bg-gray-200 rounded">Cancelar</button>
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">Guardar</button>
          </div>
        </form>
      </Modal>

      {costos.length === 0 ? (
        <p>No tienes costos registrados.</p>
      ) : (
        <table className="min-w-full bg-white">
          <thead>
            <tr>
              <th className="py-2 px-4 border-b text-left">Concepto</th>
              <th className="py-2 px-4 border-b text-left">Monto</th>
              <th className="py-2 px-4 border-b text-left">Fecha</th>
              <th className="py-2 px-4 border-b text-left">Tipo</th>
              <th className="py-2 px-4 border-b text-left">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {costos.map((costo) => (
              <tr key={costo.id}>
                <td className="py-2 px-4 border-b">{costo.concepto}</td>
                <td className="py-2 px-4 border-b">${costo.monto}</td>
                <td className="py-2 px-4 border-b">{costo.fecha}</td>
                <td className="py-2 px-4 border-b">{costo.tipo_costo}</td>
                <td className="py-2 px-4 border-b">
                  <button onClick={() => openModalForEdit(costo)} className="text-blue-500 hover:underline">Editar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default Costos;