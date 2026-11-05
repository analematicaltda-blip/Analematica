'use client';

import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useMiNegocioApi, ChartOfAccount } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/Form';
import { Input } from '@/components/ui/Input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { toast } from 'react-toastify';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { PlusCircle, Trash2 } from 'lucide-react';

const transactionSchema = z.object({
  account: z.string().min(1, 'Seleccione una cuenta.'),
  debit: z.coerce.number().min(0).default(0),
  credit: z.coerce.number().min(0).default(0),
}).refine(data => data.debit === 0 || data.credit === 0, {
  message: 'No puede haber un valor en Débito y Crédito a la vez.',
  path: ['debit'],
});

const journalEntrySchema = z.object({
  entry_date: z.string().min(1, 'La fecha es requerida.'),
  description: z.string().min(1, 'La descripción es requerida.'),
  transactions: z.array(transactionSchema).min(2, 'Debe haber al menos dos transacciones.'),
}).refine(data => {
  const totalDebit = data.transactions.reduce((acc, t) => acc + t.debit, 0);
  const totalCredit = data.transactions.reduce((acc, t) => acc + t.credit, 0);
  return totalDebit === totalCredit;
}, {
  message: 'El total de débitos debe ser igual al total de créditos.',
  path: ['transactions'],
});

type JournalEntryFormValues = z.infer<typeof journalEntrySchema>;

const NuevoAsientoPage = () => {
  const router = useRouter();
  const { createJournalEntry, getChartOfAccounts, isLoading } = useMiNegocioApi();
  const [accounts, setAccounts] = useState<ChartOfAccount[]>([]);

  const form = useForm<JournalEntryFormValues>({
    resolver: zodResolver(journalEntrySchema),
    defaultValues: {
      entry_date: new Date().toISOString().split('T')[0],
      description: '',
      transactions: [
        { account: '', debit: 0, credit: 0 },
        { account: '', debit: 0, credit: 0 },
      ],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "transactions",
  });

  useEffect(() => {
    const fetchAccounts = async () => {
      const data = await getChartOfAccounts();
      if (data) {
        // Filtrar para mostrar solo cuentas que permiten transacciones
        setAccounts(data.filter(acc => acc.allows_transactions));
      }
    };
    fetchAccounts();
  }, [getChartOfAccounts]);

  const onSubmit = async (data: JournalEntryFormValues) => {
    const formattedData = {
      ...data,
      transactions: data.transactions.map(t => ({
        ...t,
        debit: t.debit.toString(),
        credit: t.credit.toString(),
      })),
    };

    const result = await createJournalEntry(formattedData);
    if (result) {
      toast.success('Asiento contable creado con éxito.');
      router.push('/dashboard/prestador/mi-negocio/gestion-contable/contabilidad/asientos-contables');
    }
  };

  const totalDebit = form.watch('transactions').reduce((acc, t) => acc + Number(t.debit || 0), 0);
  const totalCredit = form.watch('transactions').reduce((acc, t) => acc + Number(t.credit || 0), 0);

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Nuevo Asiento Contable</h1>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
          <Card>
            <CardHeader><CardTitle>Información General</CardTitle></CardHeader>
            <CardContent className="grid md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="entry_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Fecha del Asiento</FormLabel>
                    <FormControl><Input type="date" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Descripción</FormLabel>
                    <FormControl><Input placeholder="Ej: Compra de papelería" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Transacciones</CardTitle></CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-2/5">Cuenta</TableHead>
                    <TableHead>Débito</TableHead>
                    <TableHead>Crédito</TableHead>
                    <TableHead>Acción</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {fields.map((field, index) => (
                    <TableRow key={field.id}>
                      <TableCell>
                        <FormField
                          control={form.control}
                          name={`transactions.${index}.account`}
                          render={({ field }) => (
                            <FormItem>
                               <Select onValueChange={field.onChange} defaultValue={field.value}>
                                <FormControl>
                                  <SelectTrigger>
                                    <SelectValue placeholder="Seleccione una cuenta" />
                                  </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                  {accounts.map(acc => (
                                    <SelectItem key={acc.code} value={acc.code}>
                                      {acc.code} - {acc.name}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </TableCell>
                      <TableCell>
                        <FormField
                          control={form.control}
                          name={`transactions.${index}.debit`}
                          render={({ field }) => (
                            <FormItem>
                              <FormControl><Input type="number" step="0.01" {...field} /></FormControl>
                            </FormItem>
                          )}
                        />
                      </TableCell>
                      <TableCell>
                        <FormField
                          control={form.control}
                          name={`transactions.${index}.credit`}
                          render={({ field }) => (
                            <FormItem>
                              <FormControl><Input type="number" step="0.01" {...field} /></FormControl>
                            </FormItem>
                          )}
                        />
                      </TableCell>
                      <TableCell>
                        <Button type="button" variant="destructive" size="sm" onClick={() => remove(index)} disabled={fields.length <= 2}>
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <Button type="button" variant="outline" size="sm" className="mt-4" onClick={() => append({ account: '', debit: 0, credit: 0 })}>
                <PlusCircle className="h-4 w-4 mr-2" /> Añadir Fila
              </Button>
            </CardContent>
            <div className="p-6 font-bold flex justify-end gap-8">
              <div>Total Débito: ${totalDebit.toFixed(2)}</div>
              <div>Total Crédito: ${totalCredit.toFixed(2)}</div>
            </div>
             {form.formState.errors.transactions && <p className="text-red-500 text-center pb-4">{form.formState.errors.transactions.message}</p>}
          </Card>

          <div className="flex justify-end">
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Guardando...' : 'Guardar Asiento'}
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
};

export default NuevoAsientoPage;
