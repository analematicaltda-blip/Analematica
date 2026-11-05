'use client';
import React from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { useRouter } from 'next/navigation';
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

export default function NuevoClientePage() {
  const { createCliente, isLoading } = useMiNegocioApi();
  const router = useRouter();
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>();

  const onSubmit: SubmitHandler<FormValues> = async (data) => {
    const result = await createCliente(data);
    if (result) {
      toast.success('Cliente creado con éxito');
      router.push('/dashboard/prestador/mi-negocio/gestion-operativa/genericos/clientes');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Añadir Nuevo Cliente</CardTitle>
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
            {isLoading ? 'Guardando...' : 'Guardar Cliente'}
          </Button>
        </CardFooter>
      </Card>
    </form>
  );
}
