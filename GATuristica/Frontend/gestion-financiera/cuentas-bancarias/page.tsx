'use client';

import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useMiNegocioApi, BankAccount, ChartOfAccount } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/Dialog';
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/Form';
import { Input } from '@/components/ui/Input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select';
import { Skeleton } from '@/components/ui/skeleton';
import { toast } from 'react-toastify';
import { PlusCircle } from 'lucide-react';

const bankAccountSchema = z.object({
  banco: z.string().min(1, 'El nombre del banco es requerido.'),
  numero_cuenta: z.string().min(1, 'El número de cuenta es requerido.'),
  titular: z.string().min(1, 'El titular es requerido.'),
  tipo_cuenta: z.enum(['AHORROS', 'CORRIENTE']),
  cuenta_contable: z.string().optional().nullable(),
});

type BankAccountFormValues = z.infer<typeof bankAccountSchema>;

const CuentasBancariasPage = () => {
  const { getBankAccounts, createBankAccount, getChartOfAccounts, isLoading } = useMiNegocioApi();
  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [chartOfAccounts, setChartOfAccounts] = useState<ChartOfAccount[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const form = useForm<BankAccountFormValues>({
    resolver: zodResolver(bankAccountSchema),
    defaultValues: {
      banco: '',
      numero_cuenta: '',
      titular: '',
      tipo_cuenta: 'AHORROS',
      cuenta_contable: null,
    },
  });

  const fetchBankAccounts = async () => {
    const data = await getBankAccounts();
    if (data) setAccounts(data);
  };

  useEffect(() => {
    fetchBankAccounts();
    const fetchChartOfAccounts = async () => {
      const data = await getChartOfAccounts();
      if (data) setChartOfAccounts(data.filter(acc => acc.allows_transactions));
    };
    fetchChartOfAccounts();
  }, [getBankAccounts, getChartOfAccounts]);

  const onSubmit = async (data: BankAccountFormValues) => {
    const result = await createBankAccount(data);
    if (result) {
      toast.success('Cuenta bancaria creada con éxito.');
      fetchBankAccounts(); // Recargar la lista
      setIsDialogOpen(false); // Cerrar el modal
      form.reset();
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Cuentas Bancarias</h1>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button><PlusCircle className="h-4 w-4 mr-2" />Crear Cuenta</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Nueva Cuenta Bancaria</DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                {/* Campos del formulario */}
                <FormField name="banco" control={form.control} render={({ field }) => (
                  <FormItem>
                    <FormLabel>Banco</FormLabel>
                    <FormControl><Input {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                 <FormField name="numero_cuenta" control={form.control} render={({ field }) => (
                  <FormItem>
                    <FormLabel>Número de Cuenta</FormLabel>
                    <FormControl><Input {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                 <FormField name="titular" control={form.control} render={({ field }) => (
                  <FormItem>
                    <FormLabel>Titular</FormLabel>
                    <FormControl><Input {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                <FormField name="tipo_cuenta" control={form.control} render={({ field }) => (
                  <FormItem>
                    <FormLabel>Tipo de Cuenta</FormLabel>
                     <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger><SelectValue /></SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="AHORROS">Ahorros</SelectItem>
                          <SelectItem value="CORRIENTE">Corriente</SelectItem>
                        </SelectContent>
                      </Select>
                    <FormMessage />
                  </FormItem>
                )} />
                 <FormField name="cuenta_contable" control={form.control} render={({ field }) => (
                  <FormItem>
                    <FormLabel>Cuenta Contable Asociada</FormLabel>
                     <Select onValueChange={field.onChange} defaultValue={field.value || ''}>
                        <FormControl>
                          <SelectTrigger><SelectValue placeholder="Opcional" /></SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {chartOfAccounts.map(acc => (
                             <SelectItem key={acc.code} value={acc.code}>{acc.code} - {acc.name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    <FormMessage />
                  </FormItem>
                )} />
                <Button type="submit" disabled={isLoading}>{isLoading ? 'Guardando...' : 'Guardar'}</Button>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>
      <Card>
        <CardHeader><CardTitle>Listado de Cuentas</CardTitle></CardHeader>
        <CardContent>
           {isLoading && accounts.length === 0 ? (
            <div className="space-y-2"><Skeleton className="h-10 w-full" /><Skeleton className="h-10 w-full" /></div>
          ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Banco</TableHead>
                <TableHead>Número de Cuenta</TableHead>
                <TableHead>Titular</TableHead>
                <TableHead className="text-right">Saldo</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {accounts.length > 0 ? accounts.map((acc) => (
                <TableRow key={acc.id}>
                  <TableCell>{acc.banco}</TableCell>
                  <TableCell>{acc.numero_cuenta}</TableCell>
                  <TableCell>{acc.titular}</TableCell>
                  <TableCell className="text-right">${Number(acc.saldo_actual).toFixed(2)}</TableCell>
                </TableRow>
              )) : (
                <TableRow><TableCell colSpan={4} className="text-center">No hay cuentas bancarias.</TableCell></TableRow>
              )}
            </TableBody>
          </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default CuentasBancariasPage;
