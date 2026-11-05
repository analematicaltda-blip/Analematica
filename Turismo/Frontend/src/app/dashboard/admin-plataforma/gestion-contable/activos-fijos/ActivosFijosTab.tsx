'use client';
import React, { useEffect, useState, useMemo, useCallback } from 'react';
import Link from 'next/link';
import { useMiNegocioApi, ActivoFijo, PaginatedResponse } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Input } from '@/components/ui/Input';
import { PlusCircle, Edit, Trash2 } from 'lucide-react';
import { toast } from 'react-toastify';

export default function ActivosFijosTab() {
  const { getActivosFijos, deleteActivoFijo, isLoading } = useMiNegocioApi();
  const [data, setData] = useState<PaginatedResponse<ActivoFijo> | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  const fetchActivos = useCallback(async (page: number, search: string) => {
    const response = await getActivosFijos(page, search);
    if (response) setData(response);
  }, [getActivosFijos]);

  useEffect(() => {
    const handler = setTimeout(() => fetchActivos(currentPage, searchTerm), 500);
    return () => clearTimeout(handler);
  }, [searchTerm, currentPage, fetchActivos]);

  const handleDelete = async (id: number) => {
    if (window.confirm('¿Seguro que quieres eliminar este activo?')) {
      const success = await deleteActivoFijo(id);
      if (success) {
        toast.success('Activo eliminado.');
        fetchActivos(currentPage, searchTerm);
      }
    }
  };

  const activos = useMemo(() => data?.results || [], [data]);
  const totalPages = useMemo(() => data ? Math.ceil(data.count / 10) : 0, [data]);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Lista de Activos Fijos</CardTitle>
        <Link href="/dashboard/prestador/mi-negocio/gestion-contable/activos-fijos/nuevo" passHref>
          <Button><PlusCircle className="mr-2 h-4 w-4" /> Nuevo Activo</Button>
        </Link>
      </CardHeader>
      <CardContent>
        <Input
          type="text"
          placeholder="Buscar activo..."
          value={searchTerm}
          onChange={e => { setSearchTerm(e.target.value); setCurrentPage(1); }}
          className="w-full mb-4"
        />
        {isLoading && activos.length === 0 ? <p>Cargando...</p> : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nombre</TableHead>
                  <TableHead>Categoría</TableHead>
                  <TableHead>Fecha Adquisición</TableHead>
                  <TableHead>Costo</TableHead>
                  <TableHead>Valor en Libros</TableHead>
                  <TableHead>Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {activos.map(activo => (
                  <TableRow key={activo.id}>
                    <TableCell>{activo.nombre}</TableCell>
                    <TableCell>{activo.categoria_nombre}</TableCell>
                    <TableCell>{new Date(activo.fecha_adquisicion).toLocaleDateString()}</TableCell>
                    <TableCell>{activo.costo_adquisicion}</TableCell>
                    <TableCell>{activo.valor_en_libros}</TableCell>
                    <TableCell>
                      <Link href={`/dashboard/prestador/mi-negocio/gestion-contable/activos-fijos/editar/${activo.id}`} passHref>
                        <Button variant="outline" size="sm" className="mr-2"><Edit className="h-4 w-4" /></Button>
                      </Link>
                      <Button variant="destructive" size="sm" onClick={() => handleDelete(activo.id)}><Trash2 className="h-4 w-4" /></Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <div className="flex items-center justify-end space-x-2 py-4">
              <Button variant="outline" size="sm" onClick={() => setCurrentPage(p => Math.max(p - 1, 1))} disabled={currentPage === 1 || isLoading}>Anterior</Button>
              <span>Página {currentPage} de {totalPages}</span>
              <Button variant="outline" size="sm" onClick={() => setCurrentPage(p => Math.min(p + 1, totalPages))} disabled={currentPage >= totalPages || isLoading}>Siguiente</Button>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
