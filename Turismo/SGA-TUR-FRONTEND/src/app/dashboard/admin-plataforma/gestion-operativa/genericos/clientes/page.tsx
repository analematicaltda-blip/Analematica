'use client';
import React, { useEffect, useState, useCallback, useMemo } from 'react';
import Link from 'next/link';
import { useMiNegocioApi, Cliente, PaginatedResponse } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Input } from '@/components/ui/Input';
import { PlusCircle, Edit, Trash2 } from 'lucide-react';
import { toast } from 'react-toastify';

export default function ClientesPage() {
  const { getClientes, deleteCliente, isLoading } = useMiNegocioApi();
  const [data, setData] = useState<PaginatedResponse<Cliente> | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  const fetchClientes = useCallback(async (page: number, search: string) => {
    const response = await getClientes(page, search);
    if (response) {
      setData(response);
    }
  }, [getClientes]);

  useEffect(() => {
    // Implementa un debounce para no llamar a la API en cada pulsación de tecla
    const handler = setTimeout(() => {
        fetchClientes(currentPage, searchTerm);
    }, 500); // 500ms de retraso

    return () => {
        clearTimeout(handler);
    };
  }, [searchTerm, currentPage, fetchClientes]);

  const handleDelete = async (id: number) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este cliente?')) {
      const success = await deleteCliente(id);
      if (success) {
        toast.success('Cliente eliminado con éxito');
        fetchClientes(currentPage, searchTerm); // Recargar la página actual
      }
    }
  };

  const clientes = useMemo(() => data?.results || [], [data]);
  const totalPages = useMemo(() => data ? Math.ceil(data.count / 10) : 0, [data]); // Asume 10 por página

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Gestión de Clientes</CardTitle>
        <Link href="/dashboard/prestador/mi-negocio/gestion-operativa/genericos/clientes/nuevo" passHref>
          <Button>
            <PlusCircle className="mr-2 h-4 w-4" />
            Nuevo Cliente
          </Button>
        </Link>
      </CardHeader>
      <CardContent>
        <div className="mb-4">
          <Input
            type="text"
            placeholder="Buscar por nombre, email o teléfono..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1); // Resetear a la primera página al buscar
            }}
            className="w-full"
          />
        </div>
        {isLoading && clientes.length === 0 ? (
          <p>Cargando clientes...</p>
        ) : (
          <>
            <Table>
                <TableHeader>
                <TableRow>
                    <TableHead>Nombre</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Teléfono</TableHead>
                    <TableHead>Acciones</TableHead>
                </TableRow>
                </TableHeader>
                <TableBody>
                {clientes.map((cliente) => (
                    <TableRow key={cliente.id}>
                    <TableCell>{cliente.nombre}</TableCell>
                    <TableCell>{cliente.email}</TableCell>
                    <TableCell>{cliente.telefono || 'N/A'}</TableCell>
                    <TableCell>
                        <Link href={`/dashboard/prestador/mi-negocio/gestion-operativa/genericos/clientes/editar/${cliente.id}`} passHref>
                        <Button variant="outline" size="sm" className="mr-2">
                            <Edit className="h-4 w-4" />
                        </Button>
                        </Link>
                        <Button variant="destructive" size="sm" onClick={() => handleDelete(cliente.id)}>
                        <Trash2 className="h-4 w-4" />
                        </Button>
                    </TableCell>
                    </TableRow>
                ))}
                </TableBody>
            </Table>
            <div className="flex items-center justify-end space-x-2 py-4">
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                    disabled={currentPage === 1 || isLoading}
                >
                    Anterior
                </Button>
                <span className="text-sm">Página {currentPage} de {totalPages}</span>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                    disabled={currentPage >= totalPages || isLoading}
                >
                    Siguiente
                </Button>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
