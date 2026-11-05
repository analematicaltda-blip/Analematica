'use client';

import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useMiNegocioApi, CashTransaction, BankAccount } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
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

const cashTransactionSchema = z.object({
  cuenta: z.coerce.number().min(1, 'Seleccione una cuenta.'),
  fecha: z.string().min(1, 'La fecha es requerida.'),
  tipo: z.enum(['INGRESO', 'EGRESO']),
  monto: z.coerce.number().positive('El monto debe ser positivo.'),
  descripcion: z.string().min(1, 'La descripción es requerida.'),
});

type TransactionFormValues = z.infer<typeof cashTransactionSchema>;

const TransaccionesBancariasPage = () => {
  const { getCashTransactions, createCashTransaction, getBankAccounts, isLoading } = useMiNegocioApi();
  const [transactions, setTransactions] = useState<CashTransaction[]>([]);
  const [bankAccounts, setBankAccounts] = useState<BankAccount[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const form = useForm<TransactionFormValues>({
    resolver: zodResolver(cashTransactionSchema),
    defaultValues: {
      fecha: new Date().toISOString().split('T')[0],
      descripcion: '',
      tipo: 'INGRESO',
    },
  });

  const fetchTransactions = async () => {
    const data = await getCashTransactions();
    if (data) setTransactions(data);
  };

  useEffect(() => {
    fetchTransactions();
    const fetchBankAccounts = async () => {
      const data = await getBankAccounts();
      if (data) setBankAccounts(data);
    };
    fetchBankAccounts();
  }, [getCashTransactions, getBankAccounts]);

  const onSubmit = async (data: TransactionFormValues) => {
    const formattedData = {
      ...data,
      monto: data.monto.toString(),
    };
    const result = await createCashTransaction(formattedData);
    if (result) {
      toast.success('Transacción registrada con éxito.');
      fetchTransactions();
      setIsDialogOpen(false);
      form.reset();
    }
  };

  const getAccountName = (id: number) => {
    return bankAccounts.find(acc => acc.id === id)?.banco || 'N/A';
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Transacciones Bancarias</h1>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button><PlusCircle className="h-4 w-4 mr-2" />Nueva Transacción</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Nueva Transacción</DialogTitle></DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <FormField name="cuenta" control={form.control} render={({ field }) => (
                  <FormItem>
                    <FormLabel>Cuenta Bancaria</FormLabel>
                     <Select onValueChange={field.onChange} defaultValue={String(field.value || '')}>
                        <FormControl><SelectTrigger><SelectValue placeholder="Seleccione una cuenta" /></SelectTrigger></FormControl>
                        <SelectContent>
                          {bankAccounts.map(acc => (
                             <SelectItem key={acc.id} value={String(acc.id)}>{acc.banco} - {acc.numero_cuenta}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    <FormMessage />
                  </FormItem>
                )} />
                <FormField name="fecha" control={form.control} render={({ field }) => (
                  <FormItem><FormLabel>Fecha</FormLabel><FormControl><Input type="date" {...field} /></FormControl><FormMessage /></FormItem>
                )} />
                 <FormField name="tipo" control={form.control} render={({ field }) => (
                  <FormItem>
                    <FormLabel>Tipo</FormLabel>
                     <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl><SelectTrigger><SelectValue /></SelectTrigger></FormControl>
                        <SelectContent>
                          <SelectItem value="INGRESO">Ingreso</SelectItem>
                          <SelectItem value="EGRESO">Egreso</SelectItem>
                        </SelectContent>
                      </Select>
                    <FormMessage />
                  </FormItem>
                )} />
                <FormField name="monto" control={form.control} render={({ field }) => (
                  <FormItem><FormLabel>Monto</FormLabel><FormControl><Input type="number" step="0.01" {...field} /></FormControl><FormMessage /></FormItem>
                )} />
                <FormField name="descripcion" control={form.control} render={({ field }) => (
                  <FormItem><FormLabel>Descripción</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
                )} />
                <Button type="submit" disabled={isLoading}>{isLoading ? 'Guardando...' : 'Guardar'}</Button>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>
      <Card>
        <CardHeader><CardTitle>Historial de Transacciones</CardTitle></CardHeader>
        <CardContent>
           {isLoading && transactions.length === 0 ? (
            <div className="space-y-2"><Skeleton className="h-10 w-full" /><Skeleton className="h-10 w-full" /></div>
          ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Fecha</TableHead>
                <TableHead>Cuenta</TableHead>
                <TableHead>Descripción</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead className="text-right">Monto</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {transactions.length > 0 ? transactions.map((t) => (
                <TableRow key={t.id}>
                  <TableCell>{t.fecha}</TableCell>
                  <TableCell>{getAccountName(t.cuenta)}</TableCell>
                  <TableCell>{t.descripcion}</TableCell>
                  <TableCell>{t.tipo}</TableCell>
                  <TableCell className="text-right">${Number(t.monto).toFixed(2)}</TableCell>
                </TableRow>
              )) : (
                <TableRow><TableCell colSpan={5} className="text-center">No hay transacciones.</TableCell></TableRow>
              )}
            </TableBody>
          </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default TransaccionesBancariasPage;
