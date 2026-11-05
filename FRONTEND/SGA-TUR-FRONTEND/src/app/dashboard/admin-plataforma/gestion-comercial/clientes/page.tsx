'use client';

import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useMiNegocioApi, Cliente } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/Dialog';
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/Form';
import { Input } from '@/components/ui/Input';
import { Skeleton } from '@/components/ui/skeleton';
import { toast } from 'react-toastify';
import { PlusCircle } from 'lucide-react';

const clienteSchema = z.object({
  nombre: z.string().min(1, 'El nombre es requerido.'),
  email: z.string().email('Email inválido.'),
  telefono: z.string().optional(),
});

type ClienteFormValues = z.infer<typeof clienteSchema>;

const ClientesPage = () => {
  const { getClientes, createCliente, updateCliente, isLoading } = useMiNegocioApi();
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingCliente, setEditingCliente] = useState<Cliente | null>(null);

  const form = useForm<ClienteFormValues>({
    resolver: zodResolver(clienteSchema),
  });

  const fetchClientes = async () => {
    const data = await getClientes();
    if (data) setClientes(data.results);
  };

  useEffect(() => {
    fetchClientes();
  }, []);

  useEffect(() => {
    if (editingCliente) {
      form.reset(editingCliente);
    } else {
      form.reset({ nombre: '', email: '', telefono: '' });
    }
  }, [editingCliente, form]);

  const onSubmit = async (data: ClienteFormValues) => {
    let result;
    if (editingCliente) {
      result = await updateCliente(editingCliente.id, data);
    } else {
      result = await createCliente(data);
    }

    if (result) {
      toast.success(editingCliente ? 'Cliente actualizado.' : 'Cliente creado.');
      fetchClientes();
      setIsDialogOpen(false);
      setEditingCliente(null);
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Clientes</h1>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={() => setEditingCliente(null)}><PlusCircle className="h-4 w-4 mr-2" />Crear Cliente</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{editingCliente ? 'Editar Cliente' : 'Nuevo Cliente'}</DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <FormField name="nombre" control={form.control} render={({ field }) => (
                  <FormItem><FormLabel>Nombre</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
                )} />
                <FormField name="email" control={form.control} render={({ field }) => (
                  <FormItem><FormLabel>Email</FormLabel><FormControl><Input type="email" {...field} /></FormControl><FormMessage /></FormItem>
                )} />
                <FormField name="telefono" control={form.control} render={({ field }) => (
                  <FormItem><FormLabel>Teléfono</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
                )} />
                <Button type="submit" disabled={isLoading}>{isLoading ? 'Guardando...' : 'Guardar'}</Button>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>
      <Card>
        <CardHeader><CardTitle>Listado de Clientes</CardTitle></CardHeader>
        <CardContent>
           {isLoading && clientes.length === 0 ? (
            <div className="space-y-2"><Skeleton className="h-10 w-full" /><Skeleton className="h-10 w-full" /></div>
          ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nombre</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Teléfono</TableHead>
                <TableHead>Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {clientes.length > 0 ? clientes.map((c) => (
                <TableRow key={c.id}>
                  <TableCell>{c.nombre}</TableCell>
                  <TableCell>{c.email}</TableCell>
                  <TableCell>{c.telefono}</TableCell>
                   <TableCell>
                    <Button variant="outline" size="sm" onClick={() => { setEditingCliente(c); setIsDialogOpen(true); }}>
                      Editar
                    </Button>
                  </TableCell>
                </TableRow>
              )) : (
                <TableRow><TableCell colSpan={4} className="text-center">No hay clientes registrados.</TableCell></TableRow>
              )}
            </TableBody>
          </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ClientesPage;
