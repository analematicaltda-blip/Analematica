"use client";

import { useState, useEffect, useCallback } from 'react';
import { FiPlus, FiEdit, FiTrash2, FiCheckCircle, FiClock, FiFilter } from 'react-icons/fi';
import { useAuth } from '@/contexts/AuthContext';
import {
  getAdminPublicaciones,
  deleteAdminPublicacion,
  approvePublicacion,
  AdminPublicacion,
} from '@/services/api';

// (Aquí iría un formulario modal para crear/editar, omitido por brevedad)
// const PublicacionFormModal = ({...});

export default function PublicacionManager() {
  const { user } = useAuth();
  const [publicaciones, setPublicaciones] = useState<AdminPublicacion[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  type FilterType = 'all' | 'published' | 'pending';
  const [filter, setFilter] = useState<FilterType>('pending');

  const fetchPublicaciones = useCallback(async () => {
    if (!user) return;
    setIsLoading(true);
    try {
      const esPublicado = filter === 'all' ? undefined : filter === 'published';
      const data = await getAdminPublicaciones(1, esPublicado);
      setPublicaciones(data.results);
    } catch (err) {
      setError('No se pudieron cargar las publicaciones.');
    } finally {
      setIsLoading(false);
    }
  }, [user, filter]);

  useEffect(() => {
    fetchPublicaciones();
  }, [fetchPublicaciones]);

  const handleApprove = async (id: number) => {
    try {
      await approvePublicacion(id);
      fetchPublicaciones(); // Recargar lista
    } catch {
      alert('Error al aprobar la publicación.');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteAdminPublicacion(id);
      fetchPublicaciones(); // Recargar lista
    } catch {
      alert('Error al eliminar la publicación.');
    }
  };

  const canApprove = user?.role === 'ADMIN' || user?.role === 'FUNCIONARIO_DIRECTIVO';

  if (isLoading) return <p className="text-center py-8">Cargando publicaciones...</p>;
  if (error) return <p className="text-center py-8 text-red-500">{error}</p>;

  return (
    <div className="bg-gray-50 p-4 sm:p-6 rounded-xl">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
        <h2 className="text-2xl font-bold text-gray-800">Gestión de Publicaciones</h2>
        <div className="flex items-center gap-4">
          <div className="relative">
            <FiFilter className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value as FilterType)}
              className="pl-10 pr-4 py-2 border rounded-lg"
            >
              <option value="pending">Pendientes</option>
              <option value="published">Publicadas</option>
              <option value="all">Todas</option>
            </select>
          </div>
          <button className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700">
            <FiPlus className="mr-2" />Crear Publicación
          </button>
        </div>
      </div>

      <div className="overflow-x-auto bg-white rounded-lg shadow">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Título</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipo</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Autor</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {publicaciones.map((pub) => (
              <tr key={pub.id}>
                <td className="px-6 py-4 font-medium">{pub.titulo}</td>
                <td className="px-6 py-4">{pub.tipo}</td>
                <td className="px-6 py-4 text-gray-600">{pub.autor_nombre}</td>
                <td className="px-6 py-4">
                  {pub.es_publicado ? (
                    <span className="flex items-center text-xs font-semibold text-green-800 bg-green-100 px-2 py-1 rounded-full">
                      <FiCheckCircle className="mr-1" /> Publicado
                    </span>
                  ) : (
                    <span className="flex items-center text-xs font-semibold text-yellow-800 bg-yellow-100 px-2 py-1 rounded-full">
                      <FiClock className="mr-1" /> Pendiente
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 text-right space-x-2">
                  {!pub.es_publicado && canApprove && (
                    <button onClick={() => handleApprove(pub.id)} className="px-3 py-1 text-xs text-white bg-green-600 rounded-md hover:bg-green-700">Aprobar</button>
                  )}
                  <button className="p-1 text-blue-600 hover:text-blue-900"><FiEdit /></button>
                  <button onClick={() => handleDelete(pub.id)} className="p-1 text-red-600 hover:text-red-900"><FiTrash2 /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}