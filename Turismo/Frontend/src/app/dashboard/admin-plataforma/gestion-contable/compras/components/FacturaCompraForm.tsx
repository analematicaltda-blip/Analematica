// frontend/src/app/dashboard/prestador/mi-negocio/gestion-contable/compras/components/FacturaCompraForm.tsx
'use client';
import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
// import { zodResolver } from '@hookform/resolvers/zod';
// import * as z from 'zod';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/Form';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select';
import { useMiNegocioApi, Proveedor, FacturaCompra } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';

// const formSchema = z.object({
//   proveedor: z.string().min(1, { message: "Debe seleccionar un proveedor." }),
//   number: z.string().min(1, { message: "El número es requerido." }),
//   issue_date: z.string().min(1, { message: "La fecha es requerida." }),
//   total: z.coerce.number().positive(),
// });

// type FormValues = z.infer<typeof formSchema>;
interface FormValues {
  proveedor: string;
  number: string;
  issue_date: string;
  total: number;
}

interface Props {
  onSubmit: (values: FormValues) => void;
  initialData?: Partial<FacturaCompra>;
  isSubmitting?: boolean;
}

export default function FacturaCompraForm({ onSubmit, initialData, isSubmitting }: Props) {
  const { getProveedores } = useMiNegocioApi();
  const [proveedores, setProveedores] = useState<Proveedor[]>([]);

  useEffect(() => {
    async function loadProveedores() {
      const data = await getProveedores();
      if (data && data.results) setProveedores(data.results);
    }
    loadProveedores();
  }, [getProveedores]);

  const form = useForm<FormValues>({
    // resolver: zodResolver(formSchema),
    defaultValues: {
      proveedor: initialData?.proveedor?.toString() || '',
      number: initialData?.number || '',
      issue_date: initialData?.issue_date || '',
      total: parseFloat(initialData?.total || '0'),
    },
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="proveedor"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Proveedor</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger><SelectValue placeholder="Seleccione un proveedor" /></SelectTrigger>
                </FormControl>
                <SelectContent>
                  {proveedores.map(p => <SelectItem key={p.id} value={p.id.toString()}>{p.nombre}</SelectItem>)}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="number"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Número de Factura</FormLabel>
              <FormControl><Input {...field} /></FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="issue_date"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Fecha de Emisión</FormLabel>
              <FormControl><Input type="date" {...field} /></FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="total"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Total</FormLabel>
              <FormControl><Input type="number" step="0.01" {...field} /></FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Guardando...' : 'Guardar Factura'}
        </Button>
      </form>
    </Form>
  );
}
