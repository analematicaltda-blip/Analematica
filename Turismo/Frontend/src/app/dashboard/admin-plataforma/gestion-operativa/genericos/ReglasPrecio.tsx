'use client';

import React, { useState, useEffect, useCallback } from 'react';
import api from '@/services/api';
import { useForm, SubmitHandler } from 'react-hook-form';
import Modal from '@/components/shared/Modal';
import { toast } from 'react-toastify';

interface ReglaPrecio {
  id: number;
  nombre_regla: string;
  producto_asociado: number | null;
  producto_nombre: string;
  tipo_ajuste: 'PORCENTAJE' | 'MONTO_FIJO';
  valor_ajuste: string;
  fecha_inicio: string;
  fecha_fin: string;
  activa: boolean;
}

interface Producto {
  id: number;
  nombre: string;
}

type FormInputs = Omit<ReglaPrecio, 'id' | 'producto_nombre'>;

const ReglasPrecio = () => {
  const [reglas, setReglas] = useState<ReglaPrecio[]>([]);
  const [productos, setProductos] = useState<Producto[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRegla, setEditingRegla] = useState<ReglaPrecio | null>(null);

  const { register, handleSubmit, reset, setValue } = useForm<FormInputs>();

  const fetchReglasYProductos = useCallback(async () => {
    try {
      setIsLoading(true);
      const [reglasResponse, productosResponse] = await Promise.all([
        api.get('/empresa/reglas-precio/'),
        api.get('/empresa/productos/')
      ]);
      setReglas(reglasResponse.data.results || []);
      setProductos(productosResponse.data.results || []);
    } catch (err: any) {
      setError('No se pudieron cargar los datos. ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchReglasYProductos();
  }, [fetchReglasYProductos]);

  const openModalForCreate = () => {
    reset({ nombre_regla: '', producto_asociado: null, tipo_ajuste: 'PORCENTAJE', valor_ajuste: '0.00', fecha_inicio: new Date().toISOString().split('T')[0], fecha_fin: '', activa: true });
    setEditingRegla(null);
    setIsModalOpen(true);
  };

  const openModalForEdit = (regla: ReglaPrecio) => {
    setEditingRegla(regla);
    setValue('nombre_regla', regla.nombre_regla);
    setValue('producto_asociado', regla.producto_asociado);
    setValue('tipo_ajuste', regla.tipo_ajuste);
    setValue('valor_ajuste', regla.valor_ajuste);
    setValue('fecha_inicio', regla.fecha_inicio);
    setValue('fecha_fin', regla.fecha_fin);
    setValue('activa', regla.activa);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingRegla(null);
    reset();
  };

  const onSubmit: SubmitHandler<FormInputs> = async (data) => {
    try {
      const payload = { ...data, producto_asociado: data.producto_asociado || null };
      if (editingRegla) {
        await api.patch(`/empresa/reglas-precio/${editingRegla.id}/`, payload);
        toast.success('Regla de precio actualizada con éxito');
      } else {
        await api.post('/empresa/reglas-precio/', payload);
        toast.success('Regla de precio creada con éxito');
      }
      closeModal();
      fetchReglasYProductos();
    } catch (err: any) {
      toast.error('Error al guardar la regla de precio: ' + (err.response?.data?.detail || err.message));
    }
  };

  if (isLoading) return <div>Cargando datos...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Gestión de Reglas de Precios</h1>
        <button onClick={openModalForCreate} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
          Añadir Regla
        </button>
      </div>

      <Modal isOpen={isModalOpen} onClose={closeModal} title={editingRegla ? 'Editar Regla' : 'Nueva Regla'}>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label htmlFor="nombre_regla">Nombre de la Regla</label>
            <input id="nombre_regla" {...register('nombre_regla', { required: true })} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm" />
          </div>
          <div>
            <label htmlFor="producto_asociado">Producto (Opcional)</label>
            <select id="producto_asociado" {...register('producto_asociado')} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
              <option value="">Todos los productos</option>
              {productos.map(p => <option key={p.id} value={p.id}>{p.nombre}</option>)}
            </select>
          </div>
          <div>
            <label htmlFor="tipo_ajuste">Tipo de Ajuste</label>
            <select id="tipo_ajuste" {...register('tipo_ajuste')} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
              <option value="PORCENTAJE">Porcentaje</option>
              <option value="MONTO_FIJO">Monto Fijo</option>
            </select>
          </div>
          <div>
            <label htmlFor="valor_ajuste">Valor del Ajuste</label>
            <input id="valor_ajuste" type="number" step="0.01" {...register('valor_ajuste', { required: true })} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm" />
          </div>
          <div>
            <label htmlFor="fecha_inicio">Fecha de Inicio</label>
            <input id="fecha_inicio" type="date" {...register('fecha_inicio', { required: true })} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm" />
          </div>
          <div>
            <label htmlFor="fecha_fin">Fecha de Fin</label>
            <input id="fecha_fin" type="date" {...register('fecha_fin', { required: true })} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm" />
          </div>
          <div className="flex items-center">
            <input id="activa" type="checkbox" {...register('activa')} />
            <label htmlFor="activa" className="ml-2">Activa</label>
          </div>
          <div className="flex justify-end space-x-2">
            <button type="button" onClick={closeModal}>Cancelar</button>
            <button type="submit">Guardar</button>
          </div>
        </form>
      </Modal>

      {reglas.length === 0 ? (
        <p>No tienes reglas de precios definidas.</p>
      ) : (
        <table className="min-w-full bg-white">
          <thead>
            <tr>
              <th className="py-2 px-4 border-b text-left">Nombre</th>
              <th className="py-2 px-4 border-b text-left">Producto</th>
              <th className="py-2 px-4 border-b text-left">Ajuste</th>
              <th className="py-2 px-4 border-b text-left">Activa</th>
              <th className="py-2 px-4 border-b text-left">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {reglas.map((regla) => (
              <tr key={regla.id}>
                <td className="py-2 px-4 border-b">{regla.nombre_regla}</td>
                <td className="py-2 px-4 border-b">{regla.producto_nombre || 'Todos'}</td>
                <td className="py-2 px-4 border-b">{regla.tipo_ajuste === 'PORCENTAJE' ? `${regla.valor_ajuste}%` : `$${regla.valor_ajuste}`}</td>
                <td className="py-2 px-4 border-b">{regla.activa ? 'Sí' : 'No'}</td>
                <td className="py-2 px-4 border-b">
                  <button onClick={() => openModalForEdit(regla)} className="text-blue-500 hover:underline">Editar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ReglasPrecio;