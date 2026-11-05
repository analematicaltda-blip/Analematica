// frontend/src/app/dashboard/prestador/mi-negocio/gestion-contable/inventario/components/MovimientoInventarioForm.tsx
'use client';
import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/Form';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select';
import { useMiNegocioApi, Producto } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';

const formSchema = z.object({
  producto: z.string().min(1, "Debe seleccionar un producto."),
  tipo_movimiento: z.enum(['ENTRADA', 'SALIDA', 'AJUSTE_POSITIVO', 'AJUSTE_NEGATIVO']),
  cantidad: z.coerce.number().positive(),
  descripcion: z.string().optional(),
});

type FormValues = z.infer<typeof formSchema>;

interface Props {
  onSubmit: (values: FormValues) => void;
  isSubmitting?: boolean;
}

export default function MovimientoInventarioForm({ onSubmit, isSubmitting }: Props) {
  const { getProductos } = useMiNegocioApi();
  const [productos, setProductos] = useState<Producto[]>([]);

  useEffect(() => {
    async function load() {
      const data = await getProductos();
      if(data && data.results) setProductos(data.results);
    }
    load();
  }, [getProductos]);

  const form = useForm<FormValues>({ resolver: zodResolver(formSchema) });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField name="producto" control={form.control} render={({ field }) => (
          <FormItem>
            <FormLabel>Producto</FormLabel>
            <Select onValueChange={field.onChange} defaultValue={field.value}>
              <FormControl><SelectTrigger><SelectValue placeholder="Seleccione un producto" /></SelectTrigger></FormControl>
              <SelectContent>{productos.map(p => <SelectItem key={p.id} value={p.id.toString()}>{p.nombre} ({p.sku})</SelectItem>)}</SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        )} />
        <FormField name="tipo_movimiento" control={form.control} render={({ field }) => (
          <FormItem>
            <FormLabel>Tipo de Movimiento</FormLabel>
            <Select onValueChange={field.onChange} defaultValue={field.value}>
              <FormControl><SelectTrigger><SelectValue placeholder="Seleccione un tipo" /></SelectTrigger></FormControl>
              <SelectContent>
                <SelectItem value="ENTRADA">Entrada (Compra)</SelectItem>
                <SelectItem value="SALIDA">Salida (Venta)</SelectItem>
                <SelectItem value="AJUSTE_POSITIVO">Ajuste Positivo</SelectItem>
                <SelectItem value="AJUSTE_NEGATIVO">Ajuste Negativo</SelectItem>
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        )} />
        <FormField name="cantidad" control={form.control} render={({ field }) => (
          <FormItem><FormLabel>Cantidad</FormLabel><FormControl><Input type="number" {...field} /></FormControl><FormMessage /></FormItem>
        )} />
        <FormField name="descripcion" control={form.control} render={({ field }) => (
          <FormItem><FormLabel>Descripción</FormLabel><FormControl><Textarea {...field} /></FormControl><FormMessage /></FormItem>
        )} />
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Registrando...' : 'Registrar Movimiento'}
        </Button>
      </form>
    </Form>
  );
}
