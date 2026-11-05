// frontend/src/app/dashboard/prestador/mi-negocio/gestion-archivistica/components/upload-dialog.tsx
"use client";

import { useState, ReactNode } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/services/api';

import {
    Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger
} from '@/components/ui/Dialog';
import { Button } from '@/components/ui/Button';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/Form';
import { Input } from '@/components/ui/Input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select';
import { toast } from 'react-hot-toast';
import { Loader2 } from 'lucide-react';

// Esquema de validación con Zod
const formSchema = z.object({
    title: z.string().min(3, { message: "El título debe tener al menos 3 caracteres." }),
    validity_year: z.coerce.number().min(2000, { message: "El año debe ser 2000 o posterior." }),
    process_id: z.string({ required_error: "Debe seleccionar un proceso." }),
    document_type_id: z.string({ required_error: "Debe seleccionar un tipo de documento." }),
    file: z.instanceof(FileList).refine(files => files?.length === 1, "Debe seleccionar un archivo."),
});

type UploadFormValues = z.infer<typeof formSchema>;

// Tipos para los catálogos
interface Catalog { id: string; name: string; }

// Funciones para obtener los catálogos
const fetchProcesses = async (): Promise<Catalog[]> => {
    const response = await apiClient.get('/mi-negocio/archivistica/processes/');
    return response.data.results || response.data;
};
const fetchDocumentTypes = async (): Promise<Catalog[]> => {
    const response = await apiClient.get('/mi-negocio/archivistica/document-types/');
    return response.data.results || response.data;
};

const uploadDocument = async (formData: FormData) => {
    const { data } = await apiClient.post('/mi-negocio/archivistica/documents/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
};

export function UploadDialog({ children }: { children: ReactNode }) {
    const [isOpen, setIsOpen] = useState(false);
    const queryClient = useQueryClient();

    const { data: processes, isLoading: isLoadingProcesses } = useQuery({ queryKey: ['archivisticaProcesses'], queryFn: fetchProcesses });
    const { data: documentTypes, isLoading: isLoadingDocTypes } = useQuery({ queryKey: ['archivisticaDocTypes'], queryFn: fetchDocumentTypes });

    const form = useForm<UploadFormValues>({
        resolver: zodResolver(formSchema),
    });

    const mutation = useMutation({
        mutationFn: uploadDocument,
        onSuccess: () => {
            toast.success("Documento subido. El procesamiento ha comenzado.");
            queryClient.invalidateQueries({ queryKey: ['archivisticaDocuments'] });
            setIsOpen(false);
            form.reset();
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.detail || "No se pudo subir el documento.");
        },
    });

    const onSubmit = (values: UploadFormValues) => {
        const formData = new FormData();
        formData.append('title', values.title);
        formData.append('validity_year', String(values.validity_year));
        formData.append('process_id', values.process_id);
        formData.append('document_type_id', values.document_type_id);
        formData.append('file', values.file[0]);
        mutation.mutate(formData);
    };

    return (
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <DialogTrigger asChild>{children}</DialogTrigger>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Subir Nuevo Documento</DialogTitle>
                    <DialogDescription>Complete los detalles y seleccione el archivo.</DialogDescription>
                </DialogHeader>
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                        <FormField control={form.control} name="title" render={({ field }) => (
                            <FormItem><FormLabel>Título</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
                        )} />
                        <FormField control={form.control} name="validity_year" render={({ field }) => (
                            <FormItem><FormLabel>Año de Vigencia</FormLabel><FormControl><Input type="number" {...field} /></FormControl><FormMessage /></FormItem>
                        )} />
                        <FormField control={form.control} name="process_id" render={({ field }) => (
                            <FormItem>
                                <FormLabel>Proceso</FormLabel>
                                <Select onValueChange={field.onChange} defaultValue={field.value}>
                                    <FormControl><SelectTrigger>{isLoadingProcesses ? "Cargando..." : <SelectValue placeholder="Seleccione un proceso" />}</SelectTrigger></FormControl>
                                    <SelectContent>{processes?.map(p => <SelectItem key={p.id} value={p.id}>{p.name}</SelectItem>)}</SelectContent>
                                </Select>
                                <FormMessage />
                            </FormItem>
                        )} />
                        <FormField control={form.control} name="document_type_id" render={({ field }) => (
                            <FormItem>
                                <FormLabel>Tipo de Documento</FormLabel>
                                <Select onValueChange={field.onChange} defaultValue={field.value}>
                                    <FormControl><SelectTrigger>{isLoadingDocTypes ? "Cargando..." : <SelectValue placeholder="Seleccione un tipo" />}</SelectTrigger></FormControl>
                                    <SelectContent>{documentTypes?.map(d => <SelectItem key={d.id} value={d.id}>{d.name}</SelectItem>)}</SelectContent>
                                </Select>
                                <FormMessage />
                            </FormItem>
                        )} />
                        <FormField control={form.control} name="file" render={({ field: { onChange, value, ...rest } }) => (
                            <FormItem><FormLabel>Archivo</FormLabel><FormControl><Input type="file" onChange={e => onChange(e.target.files)} {...rest} /></FormControl><FormMessage /></FormItem>
                        )} />
                        <DialogFooter>
                            <Button type="submit" disabled={mutation.isPending}>
                                {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                Subir y Procesar
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    );
}
