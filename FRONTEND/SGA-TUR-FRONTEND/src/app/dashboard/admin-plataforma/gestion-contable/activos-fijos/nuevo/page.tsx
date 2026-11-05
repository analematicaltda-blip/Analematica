'use client';
import React, { useEffect, useState } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { useRouter } from 'next/navigation';
import { useMiNegocioApi, CategoriaActivo } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Label } from '@/components/ui/Label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select';
import { toast } from 'react-toastify';

type FormValues = {
  nombre: string;
  categoria: string; // Se manejará como string por el select
  descripcion?: string;
  fecha_adquisicion: string;
  costo_adquisicion: number;
  valor_residual: number;
  vida_util_meses: number;
};

export default function NuevoActivoFijoPage() {
  const { createActivoFijo, getCategoriasActivo, isLoading } = useMiNegocioApi();
  const [categorias, setCategorias] = useState<CategoriaActivo[]>([]);
  const router = useRouter();
  const { register, handleSubmit, formState: { errors }, control } = useForm<FormValues>();

  useEffect(() => {
    // Cargar todas las categorías para el selector
    getCategoriasActivo(1, '').then(response => {
      if (response) setCategorias(response.results);
    });
  }, [getCategoriasActivo]);

  const onSubmit: SubmitHandler<FormValues> = async (data) => {
    const payload = {
      ...data,
      categoria: parseInt(data.categoria, 10), // Convertir a número
    };
    const result = await createActivoFijo(payload);
    if (result) {
      toast.success('Activo Fijo creado con éxito');
      router.push('/dashboard/prestador/mi-negocio/gestion-contable/activos-fijos');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Card className="max-w-4xl mx-auto">
        <CardHeader><CardTitle>Añadir Nuevo Activo Fijo</CardTitle></CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Columna Izquierda */}
          <div className="space-y-4">
            <div>
              <Label htmlFor="nombre">Nombre del Activo</Label>
              <Input id="nombre" {...register('nombre', { required: 'El nombre es obligatorio' })} />
              {errors.nombre && <p className="text-red-500 text-sm mt-1">{errors.nombre.message}</p>}
            </div>
            <div>
              <Label htmlFor="categoria">Categoría</Label>
                <select id="categoria" {...register('categoria', { required: 'La categoría es obligatoria' })} className="w-full p-2 border rounded">
                    <option value="">Seleccione una categoría</option>
                    {categorias.map(cat => <option key={cat.id} value={cat.id}>{cat.nombre}</option>)}
                </select>
              {errors.categoria && <p className="text-red-500 text-sm mt-1">{errors.categoria.message}</p>}
            </div>
            <div>
              <Label htmlFor="descripcion">Descripción (Opcional)</Label>
              <Input id="descripcion" {...register('descripcion')} />
            </div>
          </div>
          {/* Columna Derecha */}
          <div className="space-y-4">
            <div>
              <Label htmlFor="fecha_adquisicion">Fecha de Adquisición</Label>
              <Input type="date" id="fecha_adquisicion" {...register('fecha_adquisicion', { required: 'La fecha es obligatoria' })} />
              {errors.fecha_adquisicion && <p className="text-red-500 text-sm mt-1">{errors.fecha_adquisicion.message}</p>}
            </div>
             <div>
                <Label htmlFor="costo_adquisicion">Costo de Adquisición</Label>
                <Input type="number" step="0.01" id="costo_adquisicion" {...register('costo_adquisicion', { required: 'El costo es obligatorio', valueAsNumber: true })} />
                {errors.costo_adquisicion && <p className="text-red-500 text-sm mt-1">{errors.costo_adquisicion.message}</p>}
            </div>
             <div>
                <Label htmlFor="valor_residual">Valor Residual</Label>
                <Input type="number" step="0.01" id="valor_residual" {...register('valor_residual', { required: 'El valor es obligatorio', valueAsNumber: true })} />
                {errors.valor_residual && <p className="text-red-500 text-sm mt-1">{errors.valor_residual.message}</p>}
            </div>
            <div>
                <Label htmlFor="vida_util_meses">Vida Útil (en meses)</Label>
                <Input type="number" id="vida_util_meses" {...register('vida_util_meses', { required: 'La vida útil es obligatoria', valueAsNumber: true, min: 1 })} />
                {errors.vida_util_meses && <p className="text-red-500 text-sm mt-1">{errors.vida_util_meses.message}</p>}
            </div>
          </div>
        </CardContent>
        <CardFooter className="flex justify-end space-x-2">
           <Button type="button" variant="ghost" onClick={() => router.back()}>Cancelar</Button>
           <Button type="submit" disabled={isLoading}>{isLoading ? 'Guardando...' : 'Guardar Activo'}</Button>
        </CardFooter>
      </Card>
    </form>
  );
}
