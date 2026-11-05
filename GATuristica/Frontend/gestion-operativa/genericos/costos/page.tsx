'use client';

import React, { useState, useEffect } from 'react';
import api from '@/services/api';
import { toast } from 'react-toastify';
import { useForm, SubmitHandler } from 'react-hook-form';
import { FiTrendingDown, FiPlus, FiEdit, FiTrash2 } from 'react-icons/fi';
import { AuthGuard } from '@/components/ui/AuthGuard';
import Modal from '@/components/ui/Modal';

// --- Tipos ---
interface Costo {
  id: number;
  concepto: string;
  monto: string;
  fecha: string;
  es_recurrente: boolean;
  tipo_costo: 'FIJO' | 'VARIABLE';
}

type FormData = Omit<Costo, 'id'>;

const CostosManager = () => {
  const [costos, setCostos] = useState<Costo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCosto, setEditingCosto] = useState<Costo | null>(null);

  const { register, handleSubmit, reset, setValue } = useForm<FormData>();

  const fetchCostos = async () => {
    setIsLoading(true);
    try {
      const response = await api.get('/empresa/costos/');
      setCostos(response.data.results || response.data);
    } catch (error) {
      toast.error('No se pudieron cargar los costos.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { fetchCostos() }, []);

  const openModalForCreate = () => {
    reset();
    setEditingCosto(null);
    setIsModalOpen(true);
  };

  const openModalForEdit = (costo: Costo) => {
    setEditingCosto(costo);
    setValue('concepto', costo.concepto);
    setValue('monto', costo.monto);
    setValue('fecha', costo.fecha);
    setValue('es_recurrente', costo.es_recurrente);
    setValue('tipo_costo', costo.tipo_costo);
    setIsModalOpen(true);
  };

  const onSubmit: SubmitHandler<FormData> = async (data) => {
    const apiCall = editingCosto
      ? api.patch(`/empresa/costos/${editingCosto.id}/`, data)
      : api.post('/empresa/costos/', data);

    try {
      await apiCall;
      toast.success(`Costo ${editingCosto ? 'actualizado' : 'creado'} con éxito.`);
      fetchCostos();
      setIsModalOpen(false);
    } catch (error) {
      toast.error('Error al guardar el costo.');
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('¿Estás seguro de que deseas eliminar este registro de costo?')) {
        try {
            await api.delete(`/empresa/costos/${id}/`);
            toast.success('Costo eliminado.');
            fetchCostos();
        } catch (error) {
            toast.error('No se pudo eliminar el costo.');
        }
    }
  }

  if (isLoading) return <div>Cargando costos...</div>;

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Gestionar Costos Operativos</h1>
        <button onClick={openModalForCreate} className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
          <FiPlus className="mr-2" />
          Registrar Costo
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full bg-white">
          <thead className="bg-gray-50">
            <tr>
              <th className="py-3 px-4 text-left">Concepto</th>
              <th className="py-3 px-4 text-left">Monto</th>
              <th className="py-3 px-4 text-left">Fecha</th>
              <th className="py-3 px-4 text-left">Tipo</th>
              <th className="py-3 px-4 text-left">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {costos.map(costo => (
              <tr key={costo.id} className="border-b">
                <td className="py-3 px-4 font-medium">{costo.concepto}</td>
                <td className="py-3 px-4">${costo.monto}</td>
                <td className="py-3 px-4">{costo.fecha}</td>
                <td className="py-3 px-4">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${costo.tipo_costo === 'FIJO' ? 'bg-purple-100 text-purple-800' : 'bg-orange-100 text-orange-800'}`}>
                        {costo.tipo_costo}
                    </span>
                </td>
                <td className="py-3 px-4">
                  <button onClick={() => openModalForEdit(costo)} className="p-2 text-gray-500 hover:text-blue-600"><FiEdit /></button>
                  <button onClick={() => handleDelete(costo.id)} className="p-2 text-gray-500 hover:text-red-600"><FiTrash2 /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {costos.length === 0 && <p className="text-center py-8">No hay costos registrados.</p>}
      </div>

      {isModalOpen && (
        <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title={editingCosto ? "Editar Costo" : "Registrar Nuevo Costo"}>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <input {...register('concepto', { required: true })} placeholder="Concepto del costo" className="w-full p-2 border rounded"/>
                <input type="text" {...register('monto', { required: true })} placeholder="Monto" className="w-full p-2 border rounded"/>
                <input type="date" {...register('fecha', { required: true })} className="w-full p-2 border rounded"/>
                <select {...register('tipo_costo')} className="w-full p-2 border rounded">
                    <option value="VARIABLE">Variable</option>
                    <option value="FIJO">Fijo</option>
                </select>
                <div className="flex items-center">
                    <input type="checkbox" {...register('es_recurrente')} />
                    <label className="ml-2">Es un costo recurrente</label>
                </div>
                <button type="submit" className="w-full px-4 py-2 bg-blue-600 text-white rounded-md">Guardar</button>
            </form>
        </Modal>
      )}
    </div>
  );
};

const CostosPage = () => <AuthGuard allowedRoles={['PRESTADOR']}><CostosManager /></AuthGuard>;
export default CostosPage;