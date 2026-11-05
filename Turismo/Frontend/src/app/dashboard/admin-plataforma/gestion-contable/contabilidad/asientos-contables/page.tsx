'use client';

import { useEffect, useState } from 'react';
import { useMiNegocioApi, JournalEntry } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/skeleton';
import { toast } from 'react-toastify';
import Link from 'next/link';

const AsientosContablesPage = () => {
  const { getJournalEntries, isLoading } = useMiNegocioApi();
  const [entries, setEntries] = useState<JournalEntry[]>([]);

  useEffect(() => {
    const fetchEntries = async () => {
      const data = await getJournalEntries();
      if (data) {
        setEntries(data);
      } else {
        toast.error('No se pudieron cargar los asientos contables.');
      }
    };

    fetchEntries();
  }, [getJournalEntries]);

  const formatCurrency = (value: string | number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
    }).format(Number(value));
  };

  const calculateTotal = (transactions: any[]) => {
    return transactions.reduce((acc, curr) => acc + Number(curr.debit), 0);
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Asientos Contables</h1>
        <Link href="/dashboard/prestador/mi-negocio/gestion-contable/contabilidad/asientos-contables/nuevo" passHref>
          <Button>Crear Nuevo Asiento</Button>
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Historial de Asientos</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Fecha</TableHead>
                  <TableHead>Descripción</TableHead>
                  <TableHead className="text-right">Monto</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {entries.length > 0 ? (
                  entries.map((entry) => (
                    <TableRow key={entry.id}>
                      <TableCell className="font-medium">#{entry.id}</TableCell>
                      <TableCell>{entry.entry_date}</TableCell>
                      <TableCell>{entry.description}</TableCell>
                      <TableCell className="text-right">{formatCurrency(calculateTotal(entry.transactions))}</TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={4} className="text-center">
                      No hay asientos contables registrados.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AsientosContablesPage;
