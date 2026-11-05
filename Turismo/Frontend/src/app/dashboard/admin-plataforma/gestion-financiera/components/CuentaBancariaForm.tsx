// frontend/src/app/dashboard/prestador/mi-negocio/gestion-financiera/components/CuentaBancariaForm.tsx
'use client';
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/Form';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select';
import { BankAccount } from '../hooks/useMiNegocioApi';

const formSchema = z.object({
  banco: z.string().min(2, { message: "El nombre del banco es requerido." }),
  numero_cuenta: z.string().min(5, { message: "El número de cuenta es requerido." }),
  titular: z.string().min(2, { message: "El nombre del titular es requerido." }),
  tipo_cuenta: z.enum(['AHORROS', 'CORRIENTE']),
});

type CuentaBancariaFormValues = z.infer<typeof formSchema>;

interface Props {
  onSubmit: (values: CuentaBancariaFormValues) => void;
  initialData?: Partial<BankAccount>;
  isSubmitting?: boolean;
}

export default function CuentaBancariaForm({ onSubmit, initialData, isSubmitting }: Props) {
  const form = useForm<CuentaBancariaFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      banco: initialData?.bank_name || '',
      numero_cuenta: initialData?.account_number || '',
      titular: initialData?.account_holder || '',
      tipo_cuenta: initialData?.account_type === 'SAVINGS' ? 'AHORROS' : 'CORRIENTE',
    },
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="banco"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Nombre del Banco</FormLabel>
              <FormControl>
                <Input placeholder="Ej: Bancolombia" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="numero_cuenta"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Número de Cuenta</FormLabel>
              <FormControl>
                <Input placeholder="123-456789-00" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="titular"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Nombre del Titular</FormLabel>
              <FormControl>
                <Input placeholder="Juan Pérez" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="tipo_cuenta"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Tipo de Cuenta</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccione un tipo" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="AHORROS">Ahorros</SelectItem>
                  <SelectItem value="CORRIENTE">Corriente</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Guardando...' : 'Guardar'}
        </Button>
      </form>
    </Form>
  );
}
