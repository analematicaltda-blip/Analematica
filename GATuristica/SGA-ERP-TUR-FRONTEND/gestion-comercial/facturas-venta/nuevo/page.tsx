'use client';

import { useForm, useFieldArray, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useMiNegocioApi, Cliente, Producto } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
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

const itemSchema = z.object({
  // Contrato Estricto: El ID del producto es un UUID en formato string.
  producto_id: z.string().uuid({ message: "Debe ser un UUID válido." }),
  descripcion: z.string().min(1, "La descripción es requerida."),
  cantidad: z.coerce.number().min(1, 'La cantidad debe ser al menos 1.'),
  precio_unitario: z.coerce.number().positive('El precio debe ser positivo.'),
});

const facturaSchema = z.object({
  cliente_id: z.coerce.number().min(1, 'Seleccione un cliente.'),
  issue_date: z.string().min(1, 'La fecha es requerida.'),
  fecha_vencimiento: z.string().optional(),
  items: z.array(itemSchema).min(1, 'Debe haber al menos un ítem en la factura.'),
});

type FacturaFormValues = z.infer<typeof facturaSchema>;

const NuevaFacturaPage = () => {
  const router = useRouter();
  const { createFacturaVenta, getClientes, getProductos, isLoading } = useMiNegocioApi();
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [productos, setProductos] = useState<Producto[]>([]);

  const form = useForm<FacturaFormValues>({
    resolver: zodResolver(facturaSchema),
    defaultValues: {
      issue_date: new Date().toISOString().split('T')[0],
      fecha_vencimiento: new Date().toISOString().split('T')[0],
      items: [{ producto_id: '', descripcion: '', cantidad: 1, precio_unitario: 0 }],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "items",
  });

  const watchedItems = useWatch({ control: form.control, name: 'items' });

  useEffect(() => {
    const fetchData = async () => {
      const clientesData = await getClientes();
      if (clientesData) setClientes(clientesData.results);
      const productosData = await getProductos();
      if (productosData) setProductos(productosData.results);
    };
    fetchData();
  }, [getClientes, getProductos]);

  const handleProductChange = (productoId: string, index: number) => {
    const selectedProduct = productos.find(p => p.id === productoId);
    if (selectedProduct) {
      form.setValue(`items.${index}.precio_unitario`, Number(selectedProduct.precio_venta));
      form.setValue(`items.${index}.descripcion`, selectedProduct.nombre);
    }
  };

  // El frontend ya no calcula totales. Esta es responsabilidad del backend.
  const calculateSubtotal = () => {
    return watchedItems.reduce((acc, item) => acc + (item.cantidad * item.precio_unitario), 0);
  };
  const subtotal = calculateSubtotal();

  const onSubmit = async (data: FacturaFormValues) => {
    // El backend es la única fuente de la verdad para los cálculos.
    // El frontend solo envía los datos de entrada.
    const result = await createFacturaVenta(data);
    if (result) {
      toast.success('Factura creada con éxito. Los totales han sido calculados por el servidor.');
      router.push('/dashboard/prestador/mi-negocio/gestion-comercial/facturas-venta');
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Nueva Factura de Venta</h1>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
          <Card>
            <CardHeader><CardTitle>Información General</CardTitle></CardHeader>
            <CardContent className="grid md:grid-cols-3 gap-4">
              <FormField name="cliente_id" control={form.control} render={({ field }) => (
                <FormItem>
                  <FormLabel>Cliente</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={String(field.value || '')}>
                    <FormControl><SelectTrigger><SelectValue placeholder="Seleccione un cliente" /></SelectTrigger></FormControl>
                    <SelectContent>{clientes.map(c => <SelectItem key={c.id} value={String(c.id)}>{c.nombre}</SelectItem>)}</SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField name="issue_date" control={form.control} render={({ field }) => (
                <FormItem><FormLabel>Fecha de Emisión</FormLabel><FormControl><Input type="date" {...field} /></FormControl><FormMessage /></FormItem>
              )} />
              <FormField name="fecha_vencimiento" control={form.control} render={({ field }) => (
                <FormItem><FormLabel>Fecha de Vencimiento</FormLabel><FormControl><Input type="date" {...field} /></FormControl><FormMessage /></FormItem>
              )} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Ítems de la Factura</CardTitle></CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-2/5">Producto/Servicio</TableHead>
                    <TableHead className="w-2/5">Descripción</TableHead>
                    <TableHead>Cantidad</TableHead>
                    <TableHead>Precio Unitario</TableHead>
                    <TableHead>Subtotal Ítem</TableHead>
                    <TableHead>Acción</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {fields.map((field, index) => (
                    <TableRow key={field.id}>
                      <TableCell>
                        <FormField name={`items.${index}.producto_id`} control={form.control} render={({ field }) => (
                          <FormItem>
                            <Select onValueChange={(value) => { field.onChange(value); handleProductChange(value, index); }} defaultValue={field.value || ''}>
                              <FormControl><SelectTrigger><SelectValue placeholder="Seleccione..." /></SelectTrigger></FormControl>
                              <SelectContent>{productos.map(p => <SelectItem key={p.id} value={p.id}>{p.nombre}</SelectItem>)}</SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )} />
                      </TableCell>
                      <TableCell>
                        <FormField name={`items.${index}.descripcion`} control={form.control} render={({ field }) => (
                            <FormItem><FormControl><Input {...field} /></FormControl></FormItem>
                        )} />
                      </TableCell>
                      <TableCell>
                        <FormField name={`items.${index}.cantidad`} control={form.control} render={({ field }) => (
                          <FormItem><FormControl><Input type="number" {...field} /></FormControl></FormItem>
                        )} />
                      </TableCell>
                       <TableCell>
                        <FormField name={`items.${index}.precio_unitario`} control={form.control} render={({ field }) => (
                          <FormItem><FormControl><Input type="number" step="0.01" {...field} /></FormControl></FormItem>
                        )} />
                      </TableCell>
                      <TableCell>${(watchedItems[index].cantidad * watchedItems[index].precio_unitario).toFixed(2)}</TableCell>
                      <TableCell>
                        <Button type="button" variant="destructive" size="sm" onClick={() => remove(index)} disabled={fields.length <= 1}>
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <Button type="button" variant="outline" size="sm" className="mt-4" onClick={() => append({ producto_id: '', descripcion: '', cantidad: 1, precio_unitario: 0 })}>
                <PlusCircle className="h-4 w-4 mr-2" /> Añadir Ítem
              </Button>
            </CardContent>
             <div className="p-6 font-medium text-right space-y-2">
              {/* El frontend ya no calcula el total general. Solo muestra el subtotal de la línea de ítems como feedback visual. */}
              <div className="text-xl font-bold">Subtotal (informativo): ${subtotal.toFixed(2)}</div>
            </div>
          </Card>

          <div className="flex justify-end">
            <Button type="submit" disabled={isLoading}>{isLoading ? 'Guardando Factura...' : 'Guardar Factura'}</Button>
          </div>
        </form>
      </Form>
    </div>
  );
};

export default NuevaFacturaPage;
