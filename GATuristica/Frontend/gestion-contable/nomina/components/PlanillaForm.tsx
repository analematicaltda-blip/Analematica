// frontend/src/app/dashboard/prestador/mi-negocio/gestion-contable/nomina/components/PlanillaForm.tsx
'use client';
import React, { useState, useEffect } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/Form';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select';
import { useMiNegocioApi, Empleado, ConceptoNomina } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';

const formSchema = z.object({
  periodo_inicio: z.string(),
  periodo_fin: z.string(),
  novedades: z.array(z.object({
    empleado: z.string(),
    concepto: z.string(),
    valor: z.coerce.number(),
  })),
});

type FormValues = z.infer<typeof formSchema>;

interface Props {
  onSubmit: (values: FormValues) => void;
  isSubmitting?: boolean;
}

export default function PlanillaForm({ onSubmit, isSubmitting }: Props) {
  const { getEmpleados, getConceptosNomina } = useMiNegocioApi(); // Suponiendo que existen
  const [empleados, setEmpleados] = useState<Empleado[]>([]);
  const [conceptos, setConceptos] = useState<ConceptoNomina[]>([]); // Suponiendo tipo

  const form = useForm<FormValues>({ resolver: zodResolver(formSchema), defaultValues: { novedades: [] } });
  const { fields, append, remove } = useFieldArray({ control: form.control, name: "novedades" });

  useEffect(() => {
    async function loadData() {
      const empData = await getEmpleados();
      if(empData && empData.results) setEmpleados(empData.results);
      // const conData = await getConceptosNomina();
      // if(conData && conData.results) setConceptos(conData.results);
    }
    loadData();
  }, [getEmpleados]);

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        {/* Periodo fields */}
        {/* Novedades dynamic fields */}
        {fields.map((field, index) => (
          <div key={field.id} className="flex items-end space-x-2">
            {/* Empleado, Concepto, Valor inputs */}
            <Button type="button" variant="destructive" onClick={() => remove(index)}>X</Button>
          </div>
        ))}
        <Button type="button" onClick={() => append({ empleado: '', concepto: '', valor: 0 })}>
          Añadir Novedad
        </Button>
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Liquidando...' : 'Liquidar Planilla'}
        </Button>
      </form>
    </Form>
  );
}
