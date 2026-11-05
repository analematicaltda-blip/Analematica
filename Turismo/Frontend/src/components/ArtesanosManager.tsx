"use client";
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '@/contexts/AuthContext';
import { FiCheckCircle, FiClock, FiFilter } from 'react-icons/fi';
import CaracterizacionArtesanoForm from './CaracterizacionArtesanoForm';
import {
    getArtesanoCaracterizacionByArtesanoId,
    createArtesanoCaracterizacion,
    updateArtesanoCaracterizacion,
    CaracterizacionArtesano
} from '@/services/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface AdminArtesano {
  id: number;
  nombre_taller: string;
  nombre_artesano: string;
  aprobado: boolean;
  fecha_creacion: string;
  rubro_nombre: string;
  usuario_email: string;
}

const ArtesanosManager = () => {
  const { user, token } = useAuth();
  const [artesanos, setArtesanos] = useState<AdminArtesano[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'approved' | 'pending'>('pending');
  const [feedback, setFeedback] = useState<string | null>(null);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedArtesano, setSelectedArtesano] = useState<AdminArtesano | null>(null);
  const [caracterizacionData, setCaracterizacionData] = useState<CaracterizacionArtesano | null>(null);
  const [isReadOnly, setIsReadOnly] = useState(false);

  const fetchArtesanos = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (filter !== 'all') {
        params.append('aprobado', (filter === 'approved').toString());
      }
      const response = await axios.get(`${API_BASE_URL}/admin/artesanos/`, {
        headers: { Authorization: `Token ${token}` },
        params,
      });
      setArtesanos(response.data.results || response.data); // Adapt to paginated or non-paginated response
    } catch (err) {
      setError('No se pudo cargar la lista de artesanos.');
    } finally {
      setIsLoading(false);
    }
  }, [token, filter]);

  useEffect(() => {
    fetchArtesanos();
  }, [fetchArtesanos]);

  const handleApprove = async (id: number) => {
    if (!token || !window.confirm("¿Está seguro de que desea aprobar a este artesano?")) return;
    setError(null);
    setFeedback(null);
    try {
      await axios.patch(
        `${API_BASE_URL}/admin/artesanos/${id}/approve/`,
        {},
        { headers: { Authorization: `Token ${token}` } }
      );
      setFeedback('Artesano aprobado con éxito.');
      fetchArtesanos(); // Refresh the list
    } catch (err) {
      setError('Error al aprobar el artesano.');
    }
  };

  const handleOpenModal = async (artesano: AdminArtesano) => {
    setSelectedArtesano(artesano);
    const readOnly = user?.role === 'FUNCIONARIO_DIRECTIVO' || user?.role === 'FUNCIONARIO_PROFESIONAL';
    setIsReadOnly(readOnly);
    const data = await getArtesanoCaracterizacionByArtesanoId(artesano.id);
    setCaracterizacionData(data);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedArtesano(null);
    setCaracterizacionData(null);
    setIsReadOnly(false);
  };

  const handleFormSubmit = async (formData: FormData) => {
    if (!selectedArtesano || isReadOnly) return;
    try {
      if (caracterizacionData) {
        await updateArtesanoCaracterizacion(caracterizacionData.id, formData);
      } else {
        formData.append('artesano', String(selectedArtesano.id));
        await createArtesanoCaracterizacion(formData);
      }
      setFeedback('Caracterización guardada con éxito.');
      handleCloseModal();
    } catch (err) {
      setError('Error al guardar la caracterización.');
    }
  };

  const isFuncionario = user?.role === 'FUNCIONARIO_DIRECTIVO' || user?.role === 'FUNCIONARIO_PROFESIONAL';

  if (isLoading) return <p className="text-center py-8 text-gray-500">Cargando artesanos...</p>;
  if (error) return <p className="text-center py-8 text-red-500">{error}</p>;

  return (
    <div className="bg-gray-50 p-4 sm:p-6 rounded-xl shadow-sm">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
        <h2 className="text-2xl font-bold text-gray-800">Gestión de Artesanos</h2>
        <div className="relative">
          <FiFilter className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as 'all' | 'approved' | 'pending')}
            className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg shadow-sm bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="pending">Pendientes</option>
            <option value="approved">Aprobados</option>
            <option value="all">Todos</option>
          </select>
        </div>
      </div>

      {feedback && <div className="mb-4 p-3 bg-green-100 text-green-800 rounded-lg">{feedback}</div>}

      <div className="overflow-x-auto">
        <table className="min-w-full bg-white rounded-lg shadow overflow-hidden">
          <thead className="bg-gray-100">
            <tr>
              <th className="py-3 px-6 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Taller / Artesano</th>
              <th className="py-3 px-6 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Email</th>
              <th className="py-3 px-6 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Fecha Registro</th>
              <th className="py-3 px-6 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Estado</th>
              <th className="py-3 px-6 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {artesanos.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center py-10 text-gray-500">No hay artesanos en esta categoría.</td>
              </tr>
            ) : (
              artesanos.map((artesano) => (
                <tr key={artesano.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-900">{artesano.nombre_taller}</div>
                    <div className="text-sm text-gray-500">{artesano.nombre_artesano}</div>
                  </td>
                  <td className="py-4 px-6 whitespace-nowrap text-gray-600">{artesano.usuario_email}</td>
                  <td className="py-4 px-6 whitespace-nowrap text-gray-600">
                    {new Date(artesano.fecha_creacion).toLocaleDateString()}
                  </td>
                  <td className="py-4 px-6 whitespace-nowrap">
                    {artesano.aprobado ? (
                      <span className="flex items-center px-2.5 py-1 text-xs font-semibold text-green-800 bg-green-100 rounded-full">
                        <FiCheckCircle className="mr-1" /> Aprobado
                      </span>
                    ) : (
                      <span className="flex items-center px-2.5 py-1 text-xs font-semibold text-yellow-800 bg-yellow-100 rounded-full">
                        <FiClock className="mr-1" /> Pendiente
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap space-x-2">
                    {!artesano.aprobado && (
                      <button
                        onClick={() => handleApprove(artesano.id)}
                        className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all"
                      >
                        Aprobar
                      </button>
                    )}
                    <button
                      onClick={() => handleOpenModal(artesano)}
                      className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all"
                    >
                      {isFuncionario ? 'Ver Caracterización' : 'Editar Caracterización'}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

       {isModalOpen && selectedArtesano && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center">
            <div className="bg-white p-8 rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
                <CaracterizacionArtesanoForm
                    initialData={caracterizacionData}
                    onSubmit={handleFormSubmit}
                    onCancel={handleCloseModal}
                    artesanoId={selectedArtesano.id}
                    readOnly={isReadOnly}
                />
            </div>
        </div>
      )}
    </div>
  );
};

export default ArtesanosManager;