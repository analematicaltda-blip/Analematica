// frontend/src/app/dashboard/prestador/mi-negocio/gestion-contable/components/ChartOfAccountForm.tsx
'use client';
import React from 'react';
import { useForm } from 'react-hook-form';
import { ChartOfAccount } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
// ... (código del formulario ChartOfAccountForm)
export default function ChartOfAccountForm({ onSubmit, initialData, isLoading }) {
  const { register, handleSubmit } = useForm({ defaultValues: initialData });
  return <form onSubmit={handleSubmit(onSubmit)}>...</form>;
}
