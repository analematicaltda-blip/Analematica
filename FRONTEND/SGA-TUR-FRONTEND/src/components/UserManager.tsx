 "use client";

import { useState, useEffect, useCallback, FormEvent } from 'react';
import { FiPlus, FiEdit, FiTrash2, FiUsers } from 'react-icons/fi';
import { useAuth } from '@/contexts/AuthContext';
import {
  getUsers,
  createUser,
  updateUser,
  deleteUser,
  AdminUser,
} from '@/services/api';

// Tipos actualizados con los nuevos roles
type UserRole =
  | 'ADMIN'
  | 'FUNCIONARIO_DIRECTIVO'
  | 'FUNCIONARIO_PROFESIONAL'
  | 'PRESTADOR'
  | 'ARTESANO'
  | 'TURISTA';

interface UserFormData {
  id?: number | null;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  is_active: boolean;
  password?: string;
}

const ALL_ROLES: UserRole[] = [
  "ADMIN",
  "FUNCIONARIO_DIRECTIVO",
  "FUNCIONARIO_PROFESIONAL",
  "PRESTADOR",
  "ARTESANO",
  "TURISTA"
];

// Función para parsear errores de la API (sin cambios)
const parseApiError = (error: unknown): string => {
  if (error && typeof error === 'object' && 'response' in error) {
    const response = (error as { response: { data: unknown } }).response;
    if (response && typeof response === 'object' && 'data' in response) {
      const data = response.data;
      if (typeof data === 'object' && data !== null && !Array.isArray(data)) {
        const messages = Object.entries(data).map(([key, value]) => {
          const message = Array.isArray(value) ? value.join(', ') : String(value);
          return `${key}: ${message}`;
        });
        return messages.join('; ');
      }
      if (data && typeof data === 'object' && 'detail' in data) {
        return String((data as { detail: unknown }).detail);
      }
      return JSON.stringify(data);
    }
  }
  if (error && typeof error === 'object' && 'message' in error) {
    return String((error as { message: string }).message);
  }
  return "Ocurrió un error inesperado.";
};

// Formulario Modal Inteligente
const UserForm = ({
  onSubmit,
  onCancel,
  initialData,
  currentUserRole,
}: {
  onSubmit: (data: Partial<UserFormData>) => void;
  onCancel: () => void;
  initialData?: Partial<UserFormData> | null;
  currentUserRole: UserRole;
}) => {
  const [formData, setFormData] = useState<Partial<UserFormData>>({
    id: initialData?.id || null,
    username: initialData?.username || '',
    email: initialData?.email || '',
    first_name: initialData?.first_name || '',
    last_name: initialData?.last_name || '',
    role: initialData?.role || 'TURISTA',
    is_active: initialData?.is_active !== false,
    password: '',
  });

  // Filtra los roles que el usuario actual puede asignar
  const isFuncionario =
    currentUserRole === 'FUNCIONARIO_DIRECTIVO' ||
    currentUserRole === 'FUNCIONARIO_PROFESIONAL';

  const availableRoles =
    currentUserRole === 'ADMIN'
      ? ALL_ROLES
      : isFuncionario
      ? ALL_ROLES.filter(r => r === 'PRESTADOR' || r === 'ARTESANO' || r === 'TURISTA')
      : [];

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const dataToSend = { ...formData };
    // No enviar la contraseña si está vacía en una actualización
    if (dataToSend.id && (!dataToSend.password || dataToSend.password === '')) {
      delete dataToSend.password;
    }
    onSubmit(dataToSend);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-xl w-full max-w-lg">
        <h2 className="text-xl font-bold mb-6">{formData.id ? 'Editar' : 'Crear'} Usuario</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input type="text" name="username" value={formData.username} onChange={e => setFormData({...formData, username: e.target.value})} placeholder="Nombre de usuario" className="w-full px-3 py-2 border rounded-md" required />
          <input type="email" name="email" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} placeholder="Email" className="w-full px-3 py-2 border rounded-md" required />
          <div className="grid grid-cols-2 gap-4">
            <input type="text" name="first_name" value={formData.first_name} onChange={e => setFormData({...formData, first_name: e.target.value})} placeholder="Nombres" className="w-full px-3 py-2 border rounded-md" />
            <input type="text" name="last_name" value={formData.last_name} onChange={e => setFormData({...formData, last_name: e.target.value})} placeholder="Apellidos" className="w-full px-3 py-2 border rounded-md" />
          </div>
          <select name="role" value={formData.role} onChange={e => setFormData({...formData, role: e.target.value as UserRole})} className="w-full px-3 py-2 border rounded-md" required>
            {availableRoles.map(role => <option key={role} value={role}>{role.replace(/_/g, ' ')}</option>)}
          </select>
          <input type="password" name="password" value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} placeholder={formData.id ? "Nueva contraseña (opcional)" : "Contraseña"} className="w-full px-3 py-2 border rounded-md" required={!formData.id} />
          <div className="flex items-center">
            <input type="checkbox" id="is_active" name="is_active" checked={formData.is_active} onChange={e => setFormData({...formData, is_active: e.target.checked})} className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
            <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">Usuario Activo</label>
          </div>
          <div className="flex justify-end space-x-3 pt-4">
            <button type="button" onClick={onCancel} className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300">Cancelar</button>
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">Guardar</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default function UserManager() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<Partial<UserFormData> | null>(null);

  const fetchUsers = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getUsers();
      setUsers(response.results || []);
    } catch {
      setError("No se pudo cargar la lista de usuarios. Verifique sus permisos.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const handleOpenModal = (user?: AdminUser) => {
    setEditingUser(user ? { ...user } : null);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingUser(null);
  };

  const handleSaveUser = async (data: Partial<UserFormData>) => {
    setError(null);
    try {
      if (data.id) {
        const { id, ...updateData } = data;
        await updateUser(id, updateData);
      } else {
        const createData = data as Omit<AdminUser, 'id'>;
        await createUser(createData);
      }
      fetchUsers();
      handleCloseModal();
    } catch (err) {
      setError(`Error al guardar el usuario: ${parseApiError(err)}`);
    }
  };

  const handleDeleteUser = async (id: number) => {
    if (!window.confirm("¿Está seguro de que desea eliminar este usuario? Esta acción es irreversible.")) return;
    setError(null);
    try {
      await deleteUser(id);
      fetchUsers();
    } catch (err) {
      setError(`Error al eliminar el usuario: ${parseApiError(err)}`);
    }
  };

  if (isLoading || !currentUser) return <p className="text-center py-8 text-gray-500">Cargando usuarios...</p>;
  if (error) return <p className="text-center py-8 text-red-500">{error}</p>;

  return (
    <div className="bg-gray-50 p-4 sm:p-6 rounded-xl">
      {isModalOpen && <UserForm onSubmit={handleSaveUser} onCancel={handleCloseModal} initialData={editingUser} currentUserRole={currentUser.role as UserRole} />}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Gestión de Usuarios y Roles</h2>
        <button onClick={() => handleOpenModal()} className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 shadow-sm"><FiPlus className="mr-2" />Crear Usuario</button>
      </div>
      <div className="overflow-x-auto bg-white rounded-lg shadow">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Usuario</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rol</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
  {users.length > 0 ? users.map((user) => {
    const isFuncionario =
      currentUser.role === 'FUNCIONARIO_DIRECTIVO' ||
      currentUser.role === 'FUNCIONARIO_PROFESIONAL';

    const canManage =
      currentUser.role === 'ADMIN' ||
      (isFuncionario && ['PRESTADOR', 'ARTESANO', 'TURISTA'].includes(user.role));
              return (
                <tr key={user.id}>
                  <td className="px-6 py-4 font-medium text-gray-900">{user.username}</td>
                  <td className="px-6 py-4 text-gray-600">{user.email}</td>
                  <td className="px-6 py-4"><span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">{user.role.replace(/_/g, ' ')}</span></td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {user.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right space-x-4">
                    {canManage ? (
                      <>
                        <button onClick={() => handleOpenModal(user)} className="text-indigo-600 hover:text-indigo-900 p-1" title="Editar"><FiEdit /></button>
                        <button onClick={() => handleDeleteUser(user.id)} className="text-red-600 hover:text-red-900 p-1" title="Eliminar"><FiTrash2 /></button>
                      </>
                    ) : (
                      <span className="text-xs text-gray-400 italic">N/A</span>
                    )}
                  </td>
                </tr>
              );
            }) : (
              <tr><td colSpan={5} className="py-12 text-center text-gray-500"><FiUsers className="mx-auto h-10 w-10 text-gray-400" /><p className="mt-2">No se encontraron usuarios.</p></td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}