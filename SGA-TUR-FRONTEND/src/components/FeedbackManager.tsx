"use client";

import React, { useState, useEffect, useCallback } from 'react';
import {
  getAdminSugerencias,
  updateSugerencia,
  deleteSugerencia,
  AdminSugerencia,
} from '@/services/api';
import { FiFilter, FiTrash2, FiMessageSquare, FiThumbsUp, FiAlertTriangle } from 'react-icons/fi';

const FeedbackManager = () => {
  const [sugerencias, setSugerencias] = useState<AdminSugerencia[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState(''); // Filtro por estado

  const fetchSugerencias = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await getAdminSugerencias(filter || undefined);
      setSugerencias(response.results);
    } catch (err) {
      // Error is handled by not setting the data and letting the UI show a message.
    } finally {
      setIsLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchSugerencias();
  }, [fetchSugerencias]);

  const handleUpdate = async (id: number, data: Partial<{ estado: string; es_publico: boolean }>) => {
    try {
      await updateSugerencia(id, data);
      fetchSugerencias(); // Refresh list
    } catch {
      alert("Error al actualizar el estado.");
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("¿Está seguro de que desea eliminar este mensaje?")) return;
    try {
      await deleteSugerencia(id);
      fetchSugerencias(); // Refresh list
    } catch {
      alert("Error al eliminar el mensaje.");
    }
  };

  const getIconForType = (type: string) => {
    switch (type) {
      case 'FELICITACION': return <FiThumbsUp className="text-green-500" />;
      case 'SUGERENCIA': return <FiMessageSquare className="text-blue-500" />;
      case 'QUEJA': return <FiAlertTriangle className="text-red-500" />;
      default: return <FiMessageSquare />;
    }
  };

  return (
    <div className="bg-gray-50 p-4 sm:p-6 rounded-xl shadow-sm">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
        <h2 className="text-2xl font-bold text-gray-800">Buzón de Sugerencias y Quejas</h2>
        <div className="relative">
          <FiFilter className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg shadow-sm bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todos los Estados</option>
            <option value="RECIBIDO">Recibido</option>
            <option value="EN_REVISION">En Revisión</option>
            <option value="ATENDIDO">Atendido</option>
          </select>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full bg-white rounded-lg shadow overflow-hidden">
          <thead className="bg-gray-100">
            <tr>
              <th className="py-3 px-4 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Remitente</th>
              <th className="py-3 px-4 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Mensaje</th>
              <th className="py-3 px-4 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Tipo</th>
              <th className="py-3 px-4 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Estado</th>
              <th className="py-3 px-4 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {isLoading ? (
              <tr><td colSpan={5} className="text-center py-10">Cargando...</td></tr>
            ) : sugerencias.length === 0 ? (
              <tr><td colSpan={5} className="text-center py-10 text-gray-500">No hay mensajes.</td></tr>
            ) : (
              sugerencias.map((s) => (
                <tr key={s.id} className="hover:bg-gray-50">
                  <td className="px-4 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-900">{s.usuario?.username || s.nombre_remitente || 'Anónimo'}</div>
                    <div className="text-sm text-gray-500">{s.email_remitente}</div>
                  </td>
                  <td className="px-4 py-4"><p className="text-sm text-gray-700 line-clamp-3">{s.mensaje}</p></td>
                  <td className="px-4 py-4"><div className="flex items-center gap-2 text-sm"><span title={s.tipo_mensaje}>{getIconForType(s.tipo_mensaje)}</span> {s.tipo_mensaje}</div></td>
                  <td className="px-4 py-4">
                    <select
                        value={s.estado}
                        onChange={(e) => handleUpdate(s.id, { estado: e.target.value })}
                        className="text-sm border-gray-300 rounded-md"
                    >
                        <option value="RECIBIDO">Recibido</option>
                        <option value="EN_REVISION">En Revisión</option>
                        <option value="ATENDIDO">Atendido</option>
                    </select>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center gap-2">
                      <button onClick={() => handleUpdate(s.id, { es_publico: !s.es_publico })} className={`p-2 rounded-full transition-colors ${s.es_publico ? 'text-green-600 bg-green-100' : 'text-gray-500 hover:bg-gray-200'}`} title={s.es_publico ? 'Visible públicamente' : 'Marcar como público'}>
                        <FiThumbsUp size={16} />
                      </button>
                      <button onClick={() => handleDelete(s.id)} className="p-2 text-red-600 hover:text-red-900 hover:bg-red-100 rounded-full transition-colors" title="Eliminar">
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

export default FeedbackManager;