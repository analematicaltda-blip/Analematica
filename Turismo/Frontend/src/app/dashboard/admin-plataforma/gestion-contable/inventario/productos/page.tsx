'use client';
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useMiNegocioApi, Producto, MovimientoInventario } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/Dialog';
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/Form';
import { Input } from '@/components/ui/Input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select';
import { Skeleton } from '@/components/ui/skeleton';
import { toast } from 'react-toastify';

const ajusteSchema = z.object({
  tipo_movimiento: z.enum(['AJUSTE_POSITIVO', 'AJUSTE_NEGATIVO']),
  cantidad: z.coerce.number().positive('La cantidad debe ser positiva.'),
  descripcion: z.string().min(1, 'La descripción o motivo es requerido.'),
});
type AjusteFormValues = z.infer<typeof ajusteSchema>;

const InventarioPage = () => {
  const { getProductos, createMovimientoInventario, isLoading } = useMiNegocioApi();
  const [productos, setProductos] = useState<Producto[]>([]);
  const [selectedProducto, setSelectedProducto] = useState<Producto | null>(null);

  const form = useForm<AjusteFormValues>({ resolver: zodResolver(ajusteSchema) });

  const fetchProductos = async () => {
    const data = await getProductos();
    if (data) setProductos(data.results);
  };

  useEffect(() => { fetchProductos(); }, []);

  const onSubmit = async (data: AjusteFormValues) => {
    if (!selectedProducto) return;
    const result = await createMovimientoInventario({ ...data, producto: selectedProducto.id, almacen: 1 }); // Asumiendo almacen 1
    if (result) {
      toast.success('Ajuste de inventario realizado.');
      fetchProductos();
      setSelectedProducto(null);
      form.reset();
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Gestión de Inventario</h1>
      <Card>
        <CardHeader><CardTitle>Stock de Productos</CardTitle></CardHeader>
        <CardContent>
           {isLoading && productos.length === 0 ? (
            <div className="space-y-2"><Skeleton className="h-10 w-full" /><Skeleton className="h-10 w-full" /></div>
          ) : (
          <Table>
            <TableHeader><TableRow><TableHead>SKU</TableHead><TableHead>Nombre</TableHead><TableHead className="text-right">Stock Actual</TableHead><TableHead>Acciones</TableHead></TableRow></TableHeader>
            <TableBody>
              {productos.length > 0 ? productos.map((p) => (
                <TableRow key={p.id}>
                  <TableCell>{p.sku}</TableCell><TableCell>{p.nombre}</TableCell><TableCell className="text-right">{p.stock_actual}</TableCell>
                   <TableCell>
                    <Button variant="outline" size="sm" onClick={() => setSelectedProducto(p)}>Realizar Ajuste</Button>
                  </TableCell>
                </TableRow>
              )) : (
                <TableRow><TableCell colSpan={4} className="text-center">No hay productos en el inventario.</TableCell></TableRow>
              )}
            </TableBody>
          </Table>
          )}
        </CardContent>
      </Card>

      <Dialog open={!!selectedProducto} onOpenChange={(isOpen) => !isOpen && setSelectedProducto(null)}>
        <DialogContent>
          <DialogHeader><DialogTitle>Ajuste de Inventario para: {selectedProducto?.nombre}</DialogTitle></DialogHeader>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField name="tipo_movimiento" control={form.control} render={({ field }) => (
                <FormItem><FormLabel>Tipo de Ajuste</FormLabel>
                   <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl><SelectTrigger><SelectValue /></SelectTrigger></FormControl>
                      <SelectContent>
                        <SelectItem value="AJUSTE_POSITIVO">Ajuste Positivo (Entrada)</SelectItem>
                        <SelectItem value="AJUSTE_NEGATIVO">Ajuste Negativo (Salida)</SelectItem>
                      </SelectContent>
                    </Select>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField name="cantidad" control={form.control} render={({ field }) => (<FormItem><FormLabel>Cantidad</FormLabel><FormControl><Input type="number" {...field} /></FormControl><FormMessage /></FormItem>)} />
              <FormField name="descripcion" control={form.control} render={({ field }) => (<FormItem><FormLabel>Motivo del Ajuste</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>)} />
              <Button type="submit" disabled={isLoading}>{isLoading ? 'Guardando...' : 'Guardar Ajuste'}</Button>
            </form>
          </Form>
        </DialogContent>
      </Dialog>
    </div>
  );
};
export default InventarioPage;
