'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-toastify';
import api from '@/services/api';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { FiEdit, FiTrash2 } from 'react-icons/fi';

interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  rol_display: string;
}

const UserManager = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchUsers = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await api.get('/admin/users/');
      setUsers(response.data.results || response.data);
    } catch (error) {
      toast.error('Error al cargar los usuarios.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleDelete = async (id: number) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este usuario? Esta acción es irreversible.')) {
      try {
        await api.delete(`/admin/users/${id}/`);
        toast.success('Usuario eliminado con éxito.');
        fetchUsers();
      } catch (error) {
        toast.error('Error al eliminar el usuario.');
      }
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Gestión de Usuarios</h1>

      <div className="bg-white p-6 rounded-lg shadow-md">
        {isLoading ? (
          <p>Cargando usuarios...</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Username</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Rol</TableHead>
                <TableHead>Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell className="font-medium">{user.username}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>
                    <span className="px-2 py-1 text-xs font-semibold text-white bg-blue-500 rounded-full">
                      {user.rol_display}
                    </span>
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      <Button variant="icon" onClick={() => toast.info('La edición aún no está implementada.')}>
                        <FiEdit className="h-4 w-4" />
                      </Button>
                      <Button variant="icon" color="danger" onClick={() => handleDelete(user.id)}>
                        <FiTrash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
};

export default UserManager;