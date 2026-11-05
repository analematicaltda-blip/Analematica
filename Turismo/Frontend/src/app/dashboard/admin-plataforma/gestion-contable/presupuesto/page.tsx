'use client';
import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useMiNegocioApi, Presupuesto, PaginatedResponse } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Input } from '@/components/ui/Input';
import { PlusCircle } from 'lucide-react';

export default function PresupuestosPage() {
  const { getPresupuestos, isLoading } = useMiNegocioApi();
  const [data, setData] = useState<PaginatedResponse<Presupuesto> | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const router = useRouter();

  const fetchPresupuestos = useCallback(async (page: number, search: string) => {
    const response = await getPresupuestos(page, search);
    if (response) setData(response);
  }, [getPresupuestos]);

  useEffect(() => {
    const handler = setTimeout(() => fetchPresupuestos(currentPage, searchTerm), 500);
    return () => clearTimeout(handler);
  }, [searchTerm, currentPage, fetchPresupuestos]);

  const presupuestos = useMemo(() => data?.results || [], [data]);
  const totalPages = useMemo(() => data ? Math.ceil(data.count / 10) : 0, [data]);

  const handleRowClick = (id: number) => {
    router.push(`/dashboard/prestador/mi-negocio/gestion-contable/presupuesto/${id}`);
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Gestión de Presupuestos</CardTitle>
        {/* Placeholder para botón de crear */}
        <Button disabled><PlusCircle className="mr-2 h-4 w-4" /> Nuevo Presupuesto</Button>
      </CardHeader>
      <CardContent>
        <Input
          type="text"
          placeholder="Buscar por nombre o año..."
          value={searchTerm}
          onChange={e => { setSearchTerm(e.target.value); setCurrentPage(1); }}
          className="w-full mb-4"
        />
        {isLoading && presupuestos.length === 0 ? <p>Cargando...</p> : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nombre</TableHead>
                  <TableHead>Año Fiscal</TableHead>
                  <TableHead>Ingresos Presupuestados</TableHead>
                  <TableHead>Gastos Presupuestados</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {presupuestos.map(p => (
                  <TableRow key={p.id} onClick={() => handleRowClick(p.id)} className="cursor-pointer">
                    <TableCell>{p.nombre}</TableCell>
                    <TableCell>{p.ano_fiscal}</TableCell>
                    <TableCell>{p.total_ingresos_presupuestado}</TableCell>
                    <TableCell>{p.total_gastos_presupuestado}</TableCell>
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
