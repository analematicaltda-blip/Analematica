// frontend/src/app/dashboard/prestador/mi-negocio/gestion-contable/inventario/components/ProductoForm.tsx
'use client';
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/Form';
import { Producto } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';

const formSchema = z.object({
  nombre: z.string().min(2, "El nombre es requerido."),
  sku: z.string().min(1, "El SKU es requerido."),
  descripcion: z.string().optional(),
  costo: z.coerce.number().min(0),
  precio_venta: z.coerce.number().min(0),
  stock_minimo: z.coerce.number().min(0),
});

type FormValues = z.infer<typeof formSchema>;

interface Props {
  onSubmit: (values: FormValues) => void;
  initialData?: Partial<Producto>;
  isSubmitting?: boolean;
}

export default function ProductoForm({ onSubmit, initialData, isSubmitting }: Props) {
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      nombre: initialData?.nombre || '',
      sku: initialData?.sku || '',
      descripcion: initialData?.descripcion || '',
      costo: parseFloat(initialData?.costo || '0'),
      precio_venta: parseFloat(initialData?.precio_venta || '0'),
      stock_minimo: parseFloat(initialData?.stock_minimo || '0'),
    },
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        {/* Fields for nombre, sku, descripcion, costo, precio_venta, stock_minimo */}
        <FormField name="nombre" control={form.control} render={({ field }) => (
          <FormItem><FormLabel>Nombre</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
        )} />
        <FormField name="sku" control={form.control} render={({ field }) => (
          <FormItem><FormLabel>SKU</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
        )} />
        <FormField name="descripcion" control={form.control} render={({ field }) => (
          <FormItem><FormLabel>Descripción</FormLabel><FormControl><Textarea {...field} /></FormControl><FormMessage /></FormItem>
        )} />
        <FormField name="costo" control={form.control} render={({ field }) => (
          <FormItem><FormLabel>Costo</FormLabel><FormControl><Input type="number" step="0.01" {...field} /></FormControl><FormMessage /></FormItem>
        )} />
        <FormField name="precio_venta" control={form.control} render={({ field }) => (
          <FormItem><FormLabel>Precio de Venta</FormLabel><FormControl><Input type="number" step="0.01" {...field} /></FormControl><FormMessage /></FormItem>
        )} />
        <FormField name="stock_minimo" control={form.control} render={({ field }) => (
          <FormItem><FormLabel>Stock Mínimo</FormLabel><FormControl><Input type="number" {...field} /></FormControl><FormMessage /></FormItem>
        )} />
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Guardando...' : 'Guardar Producto'}
        </Button>
      </form>
    </Form>
  );
}
