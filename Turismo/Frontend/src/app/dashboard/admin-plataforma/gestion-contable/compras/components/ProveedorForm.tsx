// frontend/src/app/dashboard/prestador/mi-negocio/gestion-contable/compras/components/ProveedorForm.tsx
'use client';
import React from 'react';
import { useForm } from 'react-hook-form';
// import { zodResolver } from '@hookform/resolvers/zod';
// import * as z from 'zod';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/Form';
import { Proveedor } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';

// const formSchema = z.object({
//   nombre: z.string().min(2, { message: "El nombre es requerido." }),
//   identificacion: z.string().optional(),
//   telefono: z.string().optional(),
//   email: z.string().email({ message: "Email inválido." }).optional(),
//   direccion: z.string().optional(),
// });

// type ProveedorFormValues = z.infer<typeof formSchema>;
interface ProveedorFormValues {
    nombre: string;
    identificacion?: string;
    telefono?: string;
    email?: string;
    direccion?: string;
}

interface Props {
  onSubmit: (values: ProveedorFormValues) => void;
  initialData?: Partial<Proveedor>;
  isSubmitting?: boolean;
}

export default function ProveedorForm({ onSubmit, initialData, isSubmitting }: Props) {
  const form = useForm<ProveedorFormValues>({
    // resolver: zodResolver(formSchema),
    defaultValues: {
      nombre: initialData?.nombre || '',
      identificacion: initialData?.identificacion || '',
      telefono: initialData?.telefono || '',
      email: initialData?.email || '',
      direccion: initialData?.direccion || '',
    },
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="nombre"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Nombre del Proveedor</FormLabel>
              <FormControl>
                <Input placeholder="Ej: Ferretería Central" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="identificacion"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Identificación (NIT/Cédula)</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="telefono"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Teléfono</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input type="email" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="direccion"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Dirección</FormLabel>
              <FormControl>
                <Textarea {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Guardando...' : 'Guardar Proveedor'}
        </Button>
      </form>
    </Form>
  );
}
