'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { toast } from 'react-toastify';
import api from '@/services/api';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogClose,
} from '@/components/ui/Dialog';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Label } from '@/components/ui/Label';
import { Textarea } from '@/components/ui/Textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/Select';
import { Form, FormField, FormControl, FormItem, FormLabel, FormMessage } from '@/components/ui/Form';


const planSchema = z.object({
  nombre: z.string().min(3, "El nombre debe tener al menos 3 caracteres."),
  descripcion: z.string().min(10, "La descripción debe tener al menos 10 caracteres."),
  precio: z.coerce.number().positive("El precio debe ser un número positivo."),
  frecuencia: z.enum(['MENSUAL', 'SEMESTRAL', 'ANUAL']),
  tipo_usuario_objetivo: z.enum(['GOBIERNO', 'PRESTADOR']),
  is_active: z.boolean().default(true),
});

type PlanFormData = z.infer<typeof planSchema>;

interface Plan {
  id: number;
  nombre: string;
  descripcion: string;
  precio: string;
  frecuencia: string;
  tipo_usuario_objetivo: string;
  is_active: boolean;
}

interface PlanFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (plan: Plan) => void;
  planToEdit?: Plan | null;
}

export default function PlanFormModal({ isOpen, onClose, onSave, planToEdit }: PlanFormModalProps) {
  const form = useForm<PlanFormData>({
    resolver: zodResolver(planSchema),
    defaultValues: {
      nombre: '',
      descripcion: '',
      precio: 0,
      frecuencia: 'MENSUAL',
      tipo_usuario_objetivo: 'PRESTADOR',
      is_active: true,
    },
  });

  React.useEffect(() => {
    if (planToEdit) {
      form.reset({
        nombre: planToEdit.nombre,
        descripcion: planToEdit.descripcion,
        precio: parseFloat(planToEdit.precio),
        frecuencia: planToEdit.frecuencia as 'MENSUAL' | 'SEMESTRAL' | 'ANUAL',
        tipo_usuario_objetivo: planToEdit.tipo_usuario_objetivo as 'GOBIERNO' | 'PRESTADOR',
        is_active: planToEdit.is_active,
      });
    } else {
      form.reset({
        nombre: '',
        descripcion: '',
        precio: 0,
        frecuencia: 'MENSUAL',
        tipo_usuario_objetivo: 'PRESTADOR',
        is_active: true,
      });
    }
  }, [planToEdit, form]);

  if (!isOpen) return null;

  const onSubmit = async (data: PlanFormData) => {
    try {
      let response;
      if (planToEdit) {
        response = await api.put(`/admin/plataforma/planes/${planToEdit.id}/`, data);
        toast.success('Plan actualizado con éxito.');
      } else {
        response = await api.post('/admin/plataforma/planes/', data);
        toast.success('Plan creado con éxito.');
      }
      onSave(response.data);
      onClose();
    } catch (error) {
      toast.error('Error al guardar el plan.');
      console.error(error);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{planToEdit ? 'Editar Plan' : 'Crear Nuevo Plan'}</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="nombre"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nombre</FormLabel>
                  <FormControl>
                    <Input placeholder="Ej. Plan Premium" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="descripcion"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Descripción</FormLabel>
                  <FormControl>
                    <Textarea placeholder="Describe las características del plan" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="precio"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Precio</FormLabel>
                  <FormControl>
                    <Input type="number" step="0.01" placeholder="99.99" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="frecuencia"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Frecuencia</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Selecciona una frecuencia" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="MENSUAL">Mensual</SelectItem>
                        <SelectItem value="SEMESTRAL">Semestral</SelectItem>
                        <SelectItem value="ANUAL">Anual</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="tipo_usuario_objetivo"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Público Objetivo</FormLabel>
                     <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Selecciona un público" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="PRESTADOR">Prestador</SelectItem>
                        <SelectItem value="GOBIERNO">Gobierno</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <FormField
              control={form.control}
              name="is_active"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3 shadow-sm">
                  <div className="space-y-0.5">
                    <FormLabel>Activo</FormLabel>
                  </div>
                  <FormControl>
                    <input type="checkbox" checked={field.value} onChange={field.onChange} className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                  </FormControl>
                </FormItem>
              )}
            />
            <DialogFooter>
              <DialogClose asChild>
                <Button type="button" variant="secondary">Cancelar</Button>
              </DialogClose>
              <Button type="submit">Guardar</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
