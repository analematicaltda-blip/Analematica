"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { getAdminResenas, approveResena, deleteResena, AdminResena } from '@/services/api';
import { FiCheckCircle, FiClock, FiFilter, FiTrash2, FiThumbsUp, FiStar } from 'react-icons/fi';

const ResenasManager = () => {
  const [resenas, setResenas] = useState<AdminResena[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<'pending' | 'approved'>('pending');

  const fetchResenas = useCallback(async () => {
    setIsLoading(true);
    try {
      const aprobada = filter === 'approved';
      const response = await getAdminResenas(aprobada);
      setResenas(response.results);
    } catch (err) {
      // Error is handled by showing an empty list.
    } finally {
      setIsLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchResenas();
  }, [fetchResenas]);

  const handleApprove = async (id: number) => {
    if (!window.confirm("¿Está seguro de que desea aprobar esta reseña?")) return;
    try {
      await approveResena(id);
      fetchResenas(); // Refresh list
    } catch {
      alert("Error al aprobar la reseña.");
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("¿Está seguro de que desea eliminar esta reseña? Esta acción no se puede deshacer.")) return;
    try {
      await deleteResena(id);
      fetchResenas(); // Refresh list
    } catch {
      alert("Error al eliminar la reseña.");
    }
  };

  return (
    <div className="bg-gray-50 p-4 sm:p-6 rounded-xl shadow-sm">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
        <h2 className="text-2xl font-bold text-gray-800">Gestión de Reseñas</h2>
        <div className="relative">
          <FiFilter className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as 'pending' | 'approved')}
            className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg shadow-sm bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="pending">Pendientes de Aprobación</option>
            <option value="approved">Aprobadas</option>
          </select>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full bg-white rounded-lg shadow overflow-hidden">
          <thead className="bg-gray-100">
            <tr>
              <th className="py-3 px-4 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Usuario</th>
              <th className="py-3 px-4 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Comentario</th>
              <th className="py-3 px-4 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Calificación</th>
              <th className="py-3 px-4 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Estado</th>
              <th className="py-3 px-4 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {isLoading ? (
              <tr><td colSpan={5} className="text-center py-10">Cargando...</td></tr>
            ) : resenas.length === 0 ? (
              <tr><td colSpan={5} className="text-center py-10 text-gray-500">No hay reseñas en esta categoría.</td></tr>
            ) : (
              resenas.map((resena) => (
                <tr key={resena.id} className="hover:bg-gray-50">
                  <td className="px-4 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-900">{resena.usuario_nombre}</div>
                    <div className="text-sm text-gray-500">{new Date(resena.fecha_creacion).toLocaleDateString()}</div>
                  </td>
                  <td className="px-4 py-4">
                    <p className="text-sm text-gray-800 line-clamp-3">{resena.comentario}</p>
                    <p className="text-xs text-gray-500 mt-1">Sobre: {resena.content_object_repr}</p>
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center">
                      <span className="font-bold text-yellow-500 mr-1">{resena.calificacion}</span>
                      <FiStar className="text-yellow-400" fill="currentColor"/>
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    {resena.aprobada ? (
                      <span className="flex items-center px-2.5 py-1 text-xs font-semibold text-green-800 bg-green-100 rounded-full">
                        <FiCheckCircle className="mr-1" /> Aprobada
                      </span>
                    ) : (
                      <span className="flex items-center px-2.5 py-1 text-xs font-semibold text-yellow-800 bg-yellow-100 rounded-full">
                        <FiClock className="mr-1" /> Pendiente
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center gap-2">
                      {!resena.aprobada && (
                        <button onClick={() => handleApprove(resena.id)} className="p-2 text-green-600 hover:text-green-900 hover:bg-green-100 rounded-full transition-colors" title="Aprobar">
                          <FiThumbsUp size={16} />
                        </button>
                      )}
                      <button onClick={() => handleDelete(resena.id)} className="p-2 text-red-600 hover:text-red-900 hover:bg-red-100 rounded-full transition-colors" title="Eliminar">
                        <FiTrash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ResenasManager;