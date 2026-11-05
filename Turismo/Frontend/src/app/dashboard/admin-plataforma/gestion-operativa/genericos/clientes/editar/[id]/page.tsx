'use client';
import React, { useEffect } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { useRouter, useParams } from 'next/navigation';
import { useMiNegocioApi } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Label } from '@/components/ui/Label';
import { toast } from 'react-toastify';

type FormValues = {
  nombre: string;
  email: string;
  telefono?: string;
};

export default function EditarClientePage() {
  const { getClienteById, updateCliente, isLoading } = useMiNegocioApi();
  const router = useRouter();
  const params = useParams();
  const id = Number(params.id);

  const { register, handleSubmit, formState: { errors }, reset } = useForm<FormValues>();

  useEffect(() => {
    const fetchCliente = async () => {
      if (!id) return;
      const cliente = await getClienteById(id);
      if (cliente) {
        reset(cliente);
      }
    };
    fetchCliente();
  }, [id, getClienteById, reset]);

  const onSubmit: SubmitHandler<FormValues> = async (data) => {
    const result = await updateCliente(id, data);
    if (result) {
      toast.success('Cliente actualizado con éxito');
      router.push('/dashboard/prestador/mi-negocio/gestion-operativa/genericos/clientes');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Editar Cliente</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="nombre">Nombre Completo</Label>
            <Input id="nombre" {...register('nombre', { required: 'El nombre es obligatorio' })} />
            {errors.nombre && <p className="text-red-500 text-sm mt-1">{errors.nombre.message}</p>}
          </div>
          <div>
            <Label htmlFor="email">Correo Electrónico</Label>
            <Input id="email" type="email" {...register('email', {
              required: 'El email es obligatorio',
              pattern: {
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                message: 'Dirección de email inválida'
              }
            })} />
            {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>}
          </div>
          <div>
            <Label htmlFor="telefono">Teléfono (Opcional)</Label>
            <Input id="telefono" {...register('telefono')} />
          </div>
        </CardContent>
        <CardFooter className="flex justify-end space-x-2">
           <Button type="button" variant="ghost" onClick={() => router.back()}>Cancelar</Button>
           <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Guardando...' : 'Guardar Cambios'}
          </Button>
        </CardFooter>
      </Card>
    </form>
  );
}
