'use client';
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useMiNegocioApi, Proveedor } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/Dialog';
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/Form';
import { Input } from '@/components/ui/Input';
import { Skeleton } from '@/components/ui/skeleton';
import { toast } from 'react-toastify';
import { PlusCircle } from 'lucide-react';

const proveedorSchema = z.object({
  nombre: z.string().min(1, 'El nombre es requerido.'),
  identificacion: z.string().optional(),
  email: z.string().email('Email inválido.').optional().or(z.literal('')),
  telefono: z.string().optional(),
  direccion: z.string().optional(),
});

type ProveedorFormValues = z.infer<typeof proveedorSchema>;

const ProveedoresPage = () => {
  const { getProveedores, createProveedor, updateProveedor, isLoading } = useMiNegocioApi();
  const [proveedores, setProveedores] = useState<Proveedor[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingProveedor, setEditingProveedor] = useState<Proveedor | null>(null);

  const form = useForm<ProveedorFormValues>({ resolver: zodResolver(proveedorSchema) });

  const fetchProveedores = async () => {
    const data = await getProveedores();
    if (data) setProveedores(data.results);
  };

  useEffect(() => { fetchProveedores(); }, []);
  useEffect(() => {
    if (editingProveedor) form.reset(editingProveedor);
    else form.reset({ nombre: '', identificacion: '', email: '', telefono: '', direccion: '' });
  }, [editingProveedor, form]);

  const onSubmit = async (data: ProveedorFormValues) => {
    const result = editingProveedor ? await updateProveedor(editingProveedor.id, data) : await createProveedor(data);
    if (result) {
      toast.success(editingProveedor ? 'Proveedor actualizado.' : 'Proveedor creado.');
      fetchProveedores();
      setIsDialogOpen(false);
      setEditingProveedor(null);
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Proveedores</h1>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={() => setEditingProveedor(null)}><PlusCircle className="h-4 w-4 mr-2" />Crear Proveedor</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>{editingProveedor ? 'Editar' : 'Nuevo'} Proveedor</DialogTitle></DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <FormField name="nombre" control={form.control} render={({ field }) => (<FormItem><FormLabel>Nombre</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>)} />
                <FormField name="identificacion" control={form.control} render={({ field }) => (<FormItem><FormLabel>Identificación</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>)} />
                <FormField name="email" control={form.control} render={({ field }) => (<FormItem><FormLabel>Email</FormLabel><FormControl><Input type="email" {...field} /></FormControl><FormMessage /></FormItem>)} />
                <FormField name="telefono" control={form.control} render={({ field }) => (<FormItem><FormLabel>Teléfono</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>)} />
                <FormField name="direccion" control={form.control} render={({ field }) => (<FormItem><FormLabel>Dirección</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>)} />
                <Button type="submit" disabled={isLoading}>{isLoading ? 'Guardando...' : 'Guardar'}</Button>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>
      <Card>
        <CardHeader><CardTitle>Listado de Proveedores</CardTitle></CardHeader>
        <CardContent>
           {isLoading && proveedores.length === 0 ? (
            <div className="space-y-2"><Skeleton className="h-10 w-full" /><Skeleton className="h-10 w-full" /></div>
          ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nombre</TableHead><TableHead>Email</TableHead><TableHead>Teléfono</TableHead><TableHead>Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {proveedores.length > 0 ? proveedores.map((p) => (
                <TableRow key={p.id}>
                  <TableCell>{p.nombre}</TableCell><TableCell>{p.email}</TableCell><TableCell>{p.telefono}</TableCell>
                   <TableCell>
                    <Button variant="outline" size="sm" onClick={() => { setEditingProveedor(p); setIsDialogOpen(true); }}>Editar</Button>
                  </TableCell>
                </TableRow>
              )) : (
                <TableRow><TableCell colSpan={4} className="text-center">No hay proveedores registrados.</TableCell></TableRow>
              )}
            </TableBody>
          </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
export default ProveedoresPage;
