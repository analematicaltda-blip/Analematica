'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useMiNegocioApi, Proveedor } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/Form';
import { Input } from '@/components/ui/Input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select';
import { toast } from 'react-toastify';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

const facturaCompraSchema = z.object({
  proveedor: z.coerce.number().min(1, 'Seleccione un proveedor.'),
  number: z.string().min(1, 'El número de factura es requerido.'),
  issue_date: z.string().min(1, 'La fecha es requerida.'),
  fecha_vencimiento: z.string().optional(),
  total: z.coerce.number().positive('El total debe ser un número positivo.'),
  // subtotal e impuestos se pueden calcular o simplificar a solo total por ahora
});

type FacturaCompraFormValues = z.infer<typeof facturaCompraSchema>;

const NuevaFacturaCompraPage = () => {
  const router = useRouter();
  const { createFacturaCompra, getProveedores, isLoading } = useMiNegocioApi();
  const [proveedores, setProveedores] = useState<Proveedor[]>([]);

  const form = useForm<FacturaCompraFormValues>({
    resolver: zodResolver(facturaCompraSchema),
    defaultValues: {
      issue_date: new Date().toISOString().split('T')[0],
    },
  });

  useEffect(() => {
    const fetchProveedores = async () => {
      const data = await getProveedores();
      if (data) setProveedores(data.results);
    };
    fetchProveedores();
  }, [getProveedores]);

  const onSubmit = async (data: FacturaCompraFormValues) => {
    const formattedData = {
      ...data,
      total: data.total.toString(),
      subtotal: data.total.toString(), // Simplificación
      impuestos: '0', // Simplificación
    };

    const result = await createFacturaCompra(formattedData);
    if (result) {
      toast.success('Factura de compra registrada con éxito.');
      router.push('/dashboard/prestador/mi-negocio/gestion-contable/compras/facturas');
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Registrar Nueva Factura de Compra</h1>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
          <Card>
            <CardHeader><CardTitle>Información de la Factura</CardTitle></CardHeader>
            <CardContent className="grid md:grid-cols-2 gap-6">
              <FormField name="proveedor" control={form.control} render={({ field }) => (
                <FormItem>
                  <FormLabel>Proveedor</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={String(field.value || '')}>
                    <FormControl><SelectTrigger><SelectValue placeholder="Seleccione un proveedor" /></SelectTrigger></FormControl>
                    <SelectContent>{proveedores.map(p => <SelectItem key={p.id} value={String(p.id)}>{p.nombre}</SelectItem>)}</SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField name="number" control={form.control} render={({ field }) => (
                <FormItem><FormLabel>Número de Factura</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
              )} />
              <FormField name="issue_date" control={form.control} render={({ field }) => (
                <FormItem><FormLabel>Fecha de Emisión</FormLabel><FormControl><Input type="date" {...field} /></FormControl><FormMessage /></FormItem>
              )} />
              <FormField name="fecha_vencimiento" control={form.control} render={({ field }) => (
                <FormItem><FormLabel>Fecha de Vencimiento (Opcional)</FormLabel><FormControl><Input type="date" {...field} /></FormControl><FormMessage /></FormItem>
              )} />
               <FormField name="total" control={form.control} render={({ field }) => (
                <FormItem><FormLabel>Total</FormLabel><FormControl><Input type="number" step="0.01" {...field} /></FormControl><FormMessage /></FormItem>
              )} />
            </CardContent>
          </Card>

          <div className="flex justify-end">
            <Button type="submit" disabled={isLoading}>{isLoading ? 'Guardando...' : 'Guardar Factura'}</Button>
          </div>
        </form>
      </Form>
    </div>
  );
};

export default NuevaFacturaCompraPage;
