'use client';
import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { useMiNegocioApi, CategoriaActivo, PaginatedResponse } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Input } from '@/components/ui/Input';
import { PlusCircle, Edit, Trash2 } from 'lucide-react';
import { toast } from 'react-toastify';

// Podríamos tener un modal para crear/editar categorías
// Por simplicidad, por ahora solo mostramos la tabla

export default function CategoriasActivoTab() {
  const { getCategoriasActivo, deleteCategoriaActivo, isLoading } = useMiNegocioApi();
  const [data, setData] = useState<PaginatedResponse<CategoriaActivo> | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  const fetchCategorias = useCallback(async (page: number, search: string) => {
    const response = await getCategoriasActivo(page, search);
    if (response) setData(response);
  }, [getCategoriasActivo]);

  useEffect(() => {
    const handler = setTimeout(() => fetchCategorias(currentPage, searchTerm), 500);
    return () => clearTimeout(handler);
  }, [searchTerm, currentPage, fetchCategorias]);

  const handleDelete = async (id: number) => {
    if (window.confirm('¿Seguro que quieres eliminar esta categoría?')) {
      const success = await deleteCategoriaActivo(id);
      if (success) {
        toast.success('Categoría eliminada.');
        fetchCategorias(currentPage, searchTerm);
      }
    }
  };

  const categorias = useMemo(() => data?.results || [], [data]);
  const totalPages = useMemo(() => data ? Math.ceil(data.count / 10) : 0, [data]);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Categorías de Activos Fijos</CardTitle>
        {/* Placeholder para el botón de crear */}
        <Button disabled><PlusCircle className="mr-2 h-4 w-4" /> Nueva Categoría</Button>
      </CardHeader>
      <CardContent>
        <Input
          type="text"
          placeholder="Buscar categoría..."
          value={searchTerm}
          onChange={e => { setSearchTerm(e.target.value); setCurrentPage(1); }}
          className="w-full mb-4"
        />
        {isLoading && categorias.length === 0 ? <p>Cargando...</p> : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nombre</TableHead>
                  <TableHead>Descripción</TableHead>
                  <TableHead>Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {categorias.map(cat => (
                  <TableRow key={cat.id}>
                    <TableCell>{cat.nombre}</TableCell>
                    <TableCell>{cat.descripcion}</TableCell>
                    <TableCell>
                      <Button variant="outline" size="sm" className="mr-2" disabled><Edit className="h-4 w-4" /></Button>
                      <Button variant="destructive" size="sm" onClick={() => handleDelete(cat.id)}><Trash2 className="h-4 w-4" /></Button>
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
