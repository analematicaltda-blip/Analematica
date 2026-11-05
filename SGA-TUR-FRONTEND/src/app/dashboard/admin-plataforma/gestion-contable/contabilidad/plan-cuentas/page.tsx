'use client';

import { useEffect, useState } from 'react';
import { useMiNegocioApi, ChartOfAccount } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { toast } from 'react-toastify';
import { Skeleton } from '@/components/ui/skeleton';

const PlanCuentasPage = () => {
  const { getChartOfAccounts, isLoading } = useMiNegocioApi();
  const [accounts, setAccounts] = useState<ChartOfAccount[]>([]);

  useEffect(() => {
    const fetchAccounts = async () => {
      const data = await getChartOfAccounts();
      if (data) {
        setAccounts(data);
      } else {
        toast.error('No se pudo cargar el Plan de Cuentas.');
      }
    };

    fetchAccounts();
  }, [getChartOfAccounts]);

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Plan de Cuentas</h1>

      <Card>
        <CardHeader>
          <CardTitle>Listado de Cuentas Contables</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Código</TableHead>
                  <TableHead>Nombre</TableHead>
                  <TableHead>Naturaleza</TableHead>
                  <TableHead>Permite Transacciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {accounts.length > 0 ? (
                  accounts.map((account) => (
                    <TableRow key={account.code}>
                      <TableCell className="font-medium">{account.code}</TableCell>
                      <TableCell>{account.name}</TableCell>
                      <TableCell>{account.nature}</TableCell>
                      <TableCell>{account.allows_transactions ? 'Sí' : 'No'}</TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={4} className="text-center">
                      No hay cuentas contables disponibles.
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

export default PlanCuentasPage;
