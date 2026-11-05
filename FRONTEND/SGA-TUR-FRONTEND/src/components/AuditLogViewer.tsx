"use client";

import { useState, useEffect, useCallback } from 'react';
import { FiSearch, FiChevronLeft, FiChevronRight, FiFileText } from 'react-icons/fi';
import { getAuditLogs, getAuditLogActionChoices, getUsers, AuditLog, AdminUser } from '@/services/api';
import useDebounce from '@/hooks/useDebounce';

// Componente para mostrar un registro de log individual (sin cambios)
const LogDetailModal = ({ log, onClose }: { log: AuditLog, onClose: () => void }) => {
  const details = JSON.parse(log.details || '{}');
  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50" onClick={onClose}>
      <div className="bg-white p-6 rounded-lg shadow-xl w-full max-w-2xl" onClick={e => e.stopPropagation()}>
        <h3 className="text-xl font-bold mb-4">Detalles del Registro de Auditoría</h3>
        <div className="space-y-3 text-sm">
          <p><strong>ID:</strong> {log.id}</p>
          <p><strong>Usuario:</strong> {log.user.username} (ID: {log.user.id})</p>
          <p><strong>Acción:</strong> <span className="font-mono bg-gray-100 px-2 py-1 rounded">{log.action}</span></p>
          <p><strong>Fecha y Hora:</strong> {new Date(log.timestamp).toLocaleString()}</p>
          <p><strong>Objeto Modificado:</strong> {log.object_repr} (Tipo: {log.content_type}, ID: {log.object_id})</p>
          <div className="pt-2">
            <strong className="block mb-1">Detalles (JSON):</strong>
            <pre className="bg-gray-100 p-3 rounded-md text-xs overflow-auto max-h-60">{JSON.stringify(details, null, 2)}</pre>
          </div>
        </div>
        <div className="text-right mt-6">
          <button onClick={onClose} className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">Cerrar</button>
        </div>
      </div>
    </div>
  );
};

export default function AuditLogViewer() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [actionChoices, setActionChoices] = useState<{ value: string; label: string }[]>([]);

  // Estados para filtros
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterUser, setFilterUser] = useState('');
  const [filterAction, setFilterAction] = useState('');
  const debouncedSearchTerm = useDebounce(searchTerm, 500);

  const fetchLogs = useCallback(async (search: string, pageNum: number, userId: string, action: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getAuditLogs(search, pageNum, userId, action);
      setLogs(response.results);
      const totalCount = response.count;
      const pageSize = response.results.length > 0 ? response.results.length : 10;
      setTotalPages(Math.ceil(totalCount / pageSize));
    } catch {
      setError("No se pudieron cargar los registros de auditoría.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLogs(debouncedSearchTerm, page, filterUser, filterAction);
  }, [debouncedSearchTerm, page, filterUser, filterAction, fetchLogs]);

  useEffect(() => {
    // Cargar datos para los filtros
    const fetchFilterData = async () => {
      try {
        const usersResponse = await getUsers();
        setUsers(usersResponse.results || []);
        const actionsResponse = await getAuditLogActionChoices();
        setActionChoices(actionsResponse);
      } catch (err) {
      }
    };
    fetchFilterData();
  }, []);

  const handleFilterChange = (setter: React.Dispatch<React.SetStateAction<string>>) => (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => {
    setter(e.target.value);
    setPage(1);
  };

  if (error && logs.length === 0) return <p className="text-center py-8 text-red-500">{error}</p>;

  return (
    <div className="bg-gray-50 p-4 sm:p-6 rounded-xl">
      {selectedLog && <LogDetailModal log={selectedLog} onClose={() => setSelectedLog(null)} />}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
        <h2 className="text-2xl font-bold text-gray-800">Registros de Auditoría</h2>
        <div className="flex flex-wrap gap-4 w-full sm:w-auto">
          {/* Filtros */}
          <select value={filterUser} onChange={handleFilterChange(setFilterUser)} className="px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm w-full sm:w-auto">
            <option value="">Todos los Usuarios</option>
            {users.map(user => <option key={user.id} value={user.id}>{user.username}</option>)}
          </select>
          <select value={filterAction} onChange={handleFilterChange(setFilterAction)} className="px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm w-full sm:w-auto">
            <option value="">Todas las Acciones</option>
            {actionChoices.map(choice => <option key={choice.value} value={choice.value}>{choice.label}</option>)}
          </select>
          {/* Búsqueda */}
          <div className="relative w-full sm:w-auto">
            <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input type="text" placeholder="Buscar en detalles..." value={searchTerm} onChange={handleFilterChange(setSearchTerm)} className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg shadow-sm w-full" />
          </div>
        </div>
      </div>

      {isLoading ? (
        <p className="text-center py-8 text-gray-500">Cargando registros...</p>
      ) : logs.length === 0 ? (
        <div className="text-center py-12"><FiFileText className="mx-auto h-12 w-12 text-gray-400" /><h3 className="mt-2 text-sm font-medium text-gray-900">No se encontraron registros</h3><p className="mt-1 text-sm text-gray-500">Intente ajustar su búsqueda o filtros.</p></div>
      ) : (
        <>
          <div className="overflow-x-auto bg-white rounded-lg shadow">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Usuario</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acción</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Objeto</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fecha</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Detalles</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium">{log.user?.username || 'N/A'}</td>
                    <td className="px-6 py-4"><span className="font-mono text-sm bg-gray-100 px-2 py-1 rounded">{log.action}</span></td>
                    <td className="px-6 py-4 text-gray-600 truncate max-w-xs">{log.object_repr}</td>
                    <td className="px-6 py-4 text-gray-600">{new Date(log.timestamp).toLocaleString()}</td>
                    <td className="px-6 py-4 text-right">
                      <button onClick={() => setSelectedLog(log)} className="text-blue-600 hover:underline text-sm">Ver</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex justify-between items-center mt-4">
            <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1 || isLoading} className="flex items-center px-4 py-2 text-sm bg-white border rounded-md disabled:opacity-50">
              <FiChevronLeft className="mr-2"/> Anterior
            </button>
            <span className="text-sm text-gray-700">Página {page} de {totalPages}</span>
            <button onClick={() => setPage(p => p + 1)} disabled={page >= totalPages || isLoading} className="flex items-center px-4 py-2 text-sm bg-white border rounded-md disabled:opacity-50">
              Siguiente <FiChevronRight className="ml-2"/>
            </button>
          </div>
        </>
      )}
    </div>
  );
}