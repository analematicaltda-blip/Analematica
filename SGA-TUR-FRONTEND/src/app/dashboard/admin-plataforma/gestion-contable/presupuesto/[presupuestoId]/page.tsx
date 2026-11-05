'use client';
import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { useMiNegocioApi, PartidaPresupuestal, PaginatedResponse } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Input } from '@/components/ui/Input';
import { PlusCircle } from 'lucide-react';
import { useParams } from 'next/navigation';

export default function DetallePresupuestoPage() {
  const { getPartidas, isLoading } = useMiNegocioApi();
  const [data, setData] = useState<PaginatedResponse<PartidaPresupuestal> | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const params = useParams();
  const presupuestoId = parseInt(params.presupuestoId as string, 10);

  const fetchPartidas = useCallback(async (page: number, search: string) => {
    if (!presupuestoId) return;
    const response = await getPartidas(presupuestoId, page, search);
    if (response) setData(response);
  }, [getPartidas, presupuestoId]);

  useEffect(() => {
    const handler = setTimeout(() => fetchPartidas(currentPage, searchTerm), 500);
    return () => clearTimeout(handler);
  }, [searchTerm, currentPage, fetchPartidas]);

  const partidas = useMemo(() => data?.results || [], [data]);
  const totalPages = useMemo(() => data ? Math.ceil(data.count / 10) : 0, [data]);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Partidas del Presupuesto</CardTitle>
        {/* Placeholder para botón de crear */}
        <Button disabled><PlusCircle className="mr-2 h-4 w-4" /> Nueva Partida</Button>
      </CardHeader>
      <CardContent>
        <Input
          type="text"
          placeholder="Buscar por cuenta..."
          value={searchTerm}
          onChange={e => { setSearchTerm(e.target.value); setCurrentPage(1); }}
          className="w-full mb-4"
        />
        {isLoading && partidas.length === 0 ? <p>Cargando...</p> : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Cuenta Contable</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Monto Presupuestado</TableHead>
                  <TableHead>Monto Ejecutado</TableHead>
                  <TableHead>Saldo</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {partidas.map(p => (
                  <TableRow key={p.id}>
                    <TableCell>{p.cuenta_contable_nombre}</TableCell>
                    <TableCell>{p.tipo}</TableCell>
                    <TableCell>{p.monto_presupuestado}</TableCell>
                    <TableCell>{p.monto_ejecutado}</TableCell>
                    <TableCell>{(parseFloat(p.monto_presupuestado) - parseFloat(p.monto_ejecutado)).toFixed(2)}</TableCell>
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
