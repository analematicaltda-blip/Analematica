// frontend/src/app/dashboard/prestador/mi-negocio/gestion-contable/nomina/components/EmpleadoForm.tsx
'use client';
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/Form';
import { Empleado } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';

const formSchema = z.object({
  nombre: z.string().min(2),
  apellido: z.string().min(2),
  identificacion: z.string().min(5),
  email: z.string().email(),
});

type FormValues = z.infer<typeof formSchema>;

interface Props {
  onSubmit: (values: FormValues) => void;
  initialData?: Partial<Empleado>;
  isSubmitting?: boolean;
}

export default function EmpleadoForm({ onSubmit, initialData, isSubmitting }: Props) {
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      nombre: initialData?.nombre || '',
      apellido: initialData?.apellido || '',
      identificacion: initialData?.identificacion || '',
      email: initialData?.email || '',
    },
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField name="nombre" control={form.control} render={({ field }) => (
          <FormItem><FormLabel>Nombre</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
        )} />
        <FormField name="apellido" control={form.control} render={({ field }) => (
          <FormItem><FormLabel>Apellido</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
        )} />
        <FormField name="identificacion" control={form.control} render={({ field }) => (
          <FormItem><FormLabel>Identificación</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
        )} />
        <FormField name="email" control={form.control} render={({ field }) => (
          <FormItem><FormLabel>Email</FormLabel><FormControl><Input type="email" {...field} /></FormControl><FormMessage /></FormItem>
        )} />
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Guardando...' : 'Guardar Empleado'}
        </Button>
      </form>
    </Form>
  );
}
