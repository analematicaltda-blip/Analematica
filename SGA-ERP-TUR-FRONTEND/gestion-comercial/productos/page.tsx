'use client';
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useMiNegocioApi, Producto } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/Dialog';
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/Form';
import { Input } from '@/components/ui/Input';
import { Skeleton } from '@/components/ui/skeleton';
import { toast } from 'react-toastify';
import { PlusCircle } from 'lucide-react';

const productoSchema = z.object({
  nombre: z.string().min(1, 'El nombre es requerido.'),
  precio_venta: z.coerce.number().positive('El precio debe ser positivo.'),
  descripcion: z.string().optional(),
});
type ProductoFormValues = z.infer<typeof productoSchema>;

const ProductosPage = () => {
  const { getProductos, createProducto, updateProducto, deleteProducto, isLoading } = useMiNegocioApi();
  const [productos, setProductos] = useState<Producto[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingProducto, setEditingProducto] = useState<Producto | null>(null);

  const form = useForm<ProductoFormValues>({
    resolver: zodResolver(productoSchema),
  });

  const fetchProductos = async () => {
    const data = await getProductos();
    if (data) setProductos(data.results); // Asumiendo respuesta paginada
  };

  useEffect(() => {
    fetchProductos();
  }, []);

  useEffect(() => {
    if (editingProducto) form.reset({ ...editingProducto, precio_venta: Number(editingProducto.precio_venta) });
    else form.reset({ nombre: '', precio_venta: 0, descripcion: '' });
  }, [editingProducto, form]);

  const onSubmit = async (data: ProductoFormValues) => {
    const formattedData = {
      ...data,
      precio_venta: String(data.precio_venta),
      // Valores por defecto para campos no expuestos en el form simple
      costo: '0',
      stock_actual: '0',
    };
    let result;
    if (editingProducto) {
      result = await updateProducto(editingProducto.id, formattedData);
    } else {
      result = await createProducto(formattedData);
    }

    if (result) {
      toast.success(editingProducto ? 'Producto actualizado.' : 'Producto creado.');
      fetchProductos();
      setIsDialogOpen(false);
      setEditingProducto(null);
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Productos y Servicios</h1>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={() => setEditingProducto(null)}><PlusCircle className="h-4 w-4 mr-2" />Crear Producto</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>{editingProducto ? 'Editar' : 'Nuevo'} Producto/Servicio</DialogTitle></DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <FormField name="nombre" control={form.control} render={({ field }) => (
                  <FormItem><FormLabel>Nombre</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
                )} />
                <FormField name="precio_venta" control={form.control} render={({ field }) => (
                  <FormItem><FormLabel>Precio de Venta</FormLabel><FormControl><Input type="number" step="0.01" {...field} /></FormControl><FormMessage /></FormItem>
                )} />
                <FormField name="descripcion" control={form.control} render={({ field }) => (
                  <FormItem><FormLabel>Descripción</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
                )} />
                <Button type="submit" disabled={isLoading}>{isLoading ? 'Guardando...' : 'Guardar'}</Button>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>
      <Card>
        <CardHeader><CardTitle>Catálogo</CardTitle></CardHeader>
        <CardContent>
           {isLoading && productos.length === 0 ? (
            <div className="space-y-2"><Skeleton className="h-10 w-full" /><Skeleton className="h-10 w-full" /></div>
          ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nombre</TableHead>
                <TableHead>Descripción</TableHead>
                <TableHead className="text-right">Precio</TableHead>
                <TableHead>Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {productos.length > 0 ? productos.map((p) => (
                <TableRow key={p.id}>
                  <TableCell>{p.nombre}</TableCell>
                  <TableCell>{p.descripcion}</TableCell>
                  <TableCell className="text-right">${Number(p.precio_venta).toFixed(2)}</TableCell>
                   <TableCell className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => { setEditingProducto(p); setIsDialogOpen(true); }}>
                      Editar
                    </Button>
                    <Button variant="destructive" size="sm" onClick={async () => {
                      if(window.confirm('¿Eliminar producto?')) {
                        const res = await deleteProducto(p.id);
                        if(res) { toast.success('Producto eliminado'); fetchProductos(); }
                      }
                    }}>
                      Eliminar
                    </Button>
                  </TableCell>
                </TableRow>
              )) : (
                <TableRow><TableCell colSpan={4} className="text-center">No hay productos registrados.</TableCell></TableRow>
              )}
            </TableBody>
          </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ProductosPage;
