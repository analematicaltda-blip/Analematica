// frontend/src/app/dashboard/prestador/mi-negocio/gestion-contable/components/JournalEntryForm.tsx
'use client';
import React from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
// ... (código del formulario JournalEntryForm)
export default function JournalEntryForm({ onSubmit, isLoading, accounts }) {
  const { control, handleSubmit } = useForm();
  return <form onSubmit={handleSubmit(onSubmit)}>...</form>;
}
