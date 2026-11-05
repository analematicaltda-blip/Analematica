"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Atractivo, getMisAtractivos, deleteAtractivo, approveAtractivo } from '@/services/atractivoService';
import { getFormularios } from '@/services/formService';
import AtractivoForm from './AtractivoForm';
import FormFiller from './FormFiller';
import { Formulario } from '@/services/formService';
import { FiEdit, FiPlusCircle, FiTrash2, FiCheckCircle, FiFileText } from 'react-icons/fi';
import { useAuth } from '@/contexts/AuthContext';

const AtractivosManager: React.FC = () => {
  const [atractivos, setAtractivos] = useState<Atractivo[]>([]);
  const [mode, setMode] = useState<'list' | 'atractivo_form' | 'caracterizacion_form'>('list');
  const [selectedAtractivo, setSelectedAtractivo] = useState<Atractivo | undefined>(undefined);
  const [caracterizacionForm, setCaracterizacionForm] = useState<Formulario | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [atractivosData, allForms] = await Promise.all([
        getMisAtractivos(),
        getFormularios(),
      ]);
      setAtractivos(atractivosData);

      const formInfo = allForms.find(f => f.titulo === "Caracterización de Atractivo Turístico");
      if (formInfo && formInfo.id) {
        // Inconsistencia subsanada: Obtenemos el detalle completo del formulario
        const formDetail = await getFormularioDetalle(formInfo.id);
        setCaracterizacionForm(formDetail);
      } else {
        // No se hace nada si el formulario no se encuentra, es un estado válido.
      }
    } catch (err) {
      setError('No se pudieron cargar los datos necesarios.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (mode === 'list') {
      fetchData();
    }
  }, [mode, fetchData]);

  const handleCreate = () => {
    setSelectedAtractivo(undefined);
    setMode('atractivo_form');
  };

  const handleEdit = (atractivo: Atractivo) => {
    setSelectedAtractivo(atractivo);
    setMode('atractivo_form');
  };

  const handleDelete = async (slug: string) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este atractivo?')) {
      try {
        await deleteAtractivo(slug);
        fetchData(); // Recargar la lista
      } catch (err) {
        setError('Error al eliminar el atractivo.');
      }
    }
  };

  const handleApprove = async (slug: string) => {
      try {
        await approveAtractivo(slug);
        fetchData(); // Recargar la lista para mostrar el nuevo estado
      } catch (err) {
        setError('Error al aprobar el atractivo.');
      }
  };

  const handleSuccess = () => {
    setMode('list');
    fetchData();
  };

  const handleCancel = () => {
    setMode('list');
  };

  const canManage = user?.role === 'ADMIN' || user?.role === 'FUNCIONARIO_DIRECTIVO' || user?.role === 'FUNCIONARIO_PROFESIONAL';

  if (isLoading) {
    return <p>Cargando atractivos...</p>;
  }

  if (error) {
    return <p className="text-red-500">{error}</p>;
  }

  if (mode === 'atractivo_form') {
    return <AtractivoForm atractivo={selectedAtractivo} onSuccess={handleSuccess} onCancel={handleCancel} />;
  }

  if (mode === 'caracterizacion_form' && caracterizacionForm) {
    return <FormFiller form={caracterizacionForm} onBack={handleCancel} />;
  }

  return (
    <div className="bg-white p-8 rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-gray-800">Gestionar Atractivos Turísticos</h2>
        <div className="flex items-center space-x-2">
          {caracterizacionForm && (
            <button
              onClick={() => setMode('caracterizacion_form')}
              className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
            >
              <FiFileText className="mr-2" />
              Llenar Caracterización
            </button>
          )}
          <button
            onClick={handleCreate}
            className="flex items-center px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700"
          >
            <FiPlusCircle className="mr-2" />
            Crear Nuevo Atractivo
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Categoría</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
               {canManage && <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Autor</th>}
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {atractivos.map((atractivo) => (
              <tr key={atractivo.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{atractivo.nombre}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{atractivo.categoria_color}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {atractivo.es_publicado ? (
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Publicado</span>
                  ) : (
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">Pendiente</span>
                  )}
                </td>
                {canManage && <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{atractivo.autor_username || 'N/A'}</td>}
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                  {canManage && !atractivo.es_publicado && (
                      <button onClick={() => handleApprove(atractivo.slug!)} className="text-green-600 hover:text-green-900" title="Aprobar"><FiCheckCircle /></button>
                  )}
                  <button onClick={() => handleEdit(atractivo)} className="text-indigo-600 hover:text-indigo-900" title="Editar"><FiEdit /></button>
                  <button onClick={() => handleDelete(atractivo.slug!)} className="text-red-600 hover:text-red-900" title="Eliminar"><FiTrash2 /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AtractivosManager;