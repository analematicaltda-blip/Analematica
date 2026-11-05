// frontend/src/app/dashboard/prestador/mi-negocio/gestion-financiera/components/TransaccionForm.tsx
'use client';
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/Form';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select';

const formSchema = z.object({
  tipo: z.enum(['INGRESO', 'EGRESO']),
  monto: z.coerce.number().positive({ message: "El monto debe ser un número positivo." }),
  descripcion: z.string().min(2, { message: "La descripción es requerida." }),
});

type TransaccionFormValues = z.infer<typeof formSchema>;

interface Props {
  onSubmit: (values: TransaccionFormValues) => void;
  isSubmitting?: boolean;
}

export default function TransaccionForm({ onSubmit, isSubmitting }: Props) {
  const form = useForm<TransaccionFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      tipo: 'INGRESO',
      monto: 0,
      descripcion: '',
    },
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="tipo"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Tipo de Transacción</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="INGRESO">Ingreso</SelectItem>
                  <SelectItem value="EGRESO">Egreso</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="monto"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Monto</FormLabel>
              <FormControl>
                <Input type="number" step="0.01" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="descripcion"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Descripción</FormLabel>
              <FormControl>
                <Textarea placeholder="Ej: Pago de servicios" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Guardando...' : 'Guardar Transacción'}
        </Button>
      </form>
    </Form>
  );
}
