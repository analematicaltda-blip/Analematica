"use client";

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';
import { useForm, useFieldArray } from 'react-hook-form';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { FiSave, FiPlus, FiTrash2, FiArrowLeft } from 'react-icons/fi';
import { Categoria } from '@/services/api';

// Interfaces
interface ItemData {
    id?: number;
    texto_requisito: string;
    puntaje: number;
    es_obligatorio: boolean;
}

interface PlantillaData {
    nombre: string;
    descripcion: string;
    categoria_prestador: number | null;
    items: ItemData[];
}

const VerificacionFormPage = () => {
    const { token } = useAuth();
    const router = useRouter();
    const params = useParams();
    const id = params.id as string;
    const isCreating = id === 'crear';

    const [isLoading, setIsLoading] = useState(!isCreating);
    const [categorias, setCategorias] = useState<Categoria[]>([]);

    const { register, control, handleSubmit, reset } = useForm<PlantillaData>({
        defaultValues: { items: [] }
    });

    const { fields, append, remove } = useFieldArray({ control, name: "items" });

    const apiClient = axios.create({
        baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
        headers: { Authorization: `Token ${token}` }
    });

    // Cargar categorías
    useEffect(() => {
        apiClient.get('/prestadores/categorias/')
            .then(res => setCategorias(res.data))
            .catch(() => toast.error("No se pudieron cargar las categorías."));
    }, [apiClient]);

    // Cargar datos de la plantilla si se está editando
    useEffect(() => {
        if (!isCreating && token) {
            setIsLoading(true);
            apiClient.get(`/plantillas-verificacion/${id}/`)
                .then(res => reset(res.data))
                .catch(() => toast.error("Error al cargar la plantilla."))
                .finally(() => setIsLoading(false));
        }
    }, [id, token, isCreating, reset, apiClient]);

    const onSubmit = async (data: PlantillaData) => {
        const toastId = toast.loading(isCreating ? "Creando plantilla..." : "Actualizando plantilla...");
        try {
            // La API espera un `ViewSet` completo, por lo que podemos enviar los datos directamente.
            const url = isCreating ? '/plantillas-verificacion/' : `/plantillas-verificacion/${id}/`;
            const method = isCreating ? 'post' : 'patch';
            await apiClient({ method, url, data });
            toast.update(toastId, { render: "Plantilla guardada con éxito.", type: "success", isLoading: false, autoClose: 3000 });
            router.push('/dashboard/formularios');
        } catch {
            toast.update(toastId, { render: "Error al guardar la plantilla.", type: "error", isLoading: false, autoClose: 5000 });
        }
    };

    if (isLoading) return <p>Cargando plantilla...</p>;

    return (
        <div className="container mx-auto">
            <ToastContainer />
            <Link href="/dashboard/formularios" className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-6">
                <FiArrowLeft className="mr-2" /> Volver
            </Link>
            <h1 className="text-3xl font-bold text-gray-800 mb-6">
                {isCreating ? 'Crear Plantilla de Verificación' : 'Editar Plantilla'}
            </h1>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
                {/* Detalles de la Plantilla */}
                <div className="bg-white p-6 rounded-lg shadow-md space-y-4">
                    <h2 className="text-xl font-semibold">Detalles de la Plantilla</h2>
                    <div>
                        <label className="block text-sm font-medium">Nombre</label>
                        <input {...register('nombre', { required: true })} className="mt-1 block w-full rounded-md border-gray-300"/>
                    </div>
                    <div>
                        <label className="block text-sm font-medium">Descripción</label>
                        <textarea {...register('descripcion')} rows={3} className="mt-1 block w-full rounded-md border-gray-300"/>
                    </div>
                     <div>
                        <label className="block text-sm font-medium">Asociar a Categoría</label>
                        <select {...register('categoria_prestador')} className="mt-1 block w-full rounded-md border-gray-300">
                            <option value="">Ninguna</option>
                            {categorias.map(cat => <option key={cat.id} value={cat.id}>{cat.nombre}</option>)}
                        </select>
                    </div>
                </div>

                {/* Ítems de Verificación */}
                <div className="bg-white p-6 rounded-lg shadow-md space-y-4">
                    <h2 className="text-xl font-semibold">Ítems del Checklist</h2>
                    {fields.map((field, index) => (
                        <div key={field.id} className="border p-4 rounded-lg space-y-3 bg-gray-50">
                            <div className="flex justify-between items-start">
                                <div className="flex-grow">
                                    <label className="block text-sm font-medium">Texto del Requisito</label>
                                    <input {...register(`items.${index}.texto_requisito`, { required: true })} className="mt-1 block w-full rounded-md border-gray-300"/>
                                </div>
                                <button type="button" onClick={() => remove(index)} className="ml-4 text-red-500 hover:text-red-700"><FiTrash2/></button>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium">Puntaje</label>
                                    <input type="number" {...register(`items.${index}.puntaje`)} className="mt-1 block w-full rounded-md border-gray-300"/>
                                </div>
                                <div className="flex items-end">
                                    <input type="checkbox" {...register(`items.${index}.es_obligatorio`)} className="h-4 w-4 rounded border-gray-300" />
                                    <label className="ml-2 block text-sm">Es obligatorio</label>
                                </div>
                            </div>
                        </div>
                    ))}
                    <button type="button" onClick={() => append({ texto_requisito: '', puntaje: 5, es_obligatorio: true })}
                        className="inline-flex items-center px-4 py-2 border border-dashed text-sm font-medium rounded-md text-blue-700 hover:bg-blue-50">
                        <FiPlus className="mr-2"/> Añadir Ítem
                    </button>
                </div>

                <div className="flex justify-end">
                    <button type="submit" className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-bold rounded-lg shadow-md hover:bg-blue-700">
                        <FiSave className="mr-2"/> Guardar Plantilla
                    </button>
                </div>
            </form>
        </div>
    );
};

export default VerificacionFormPage;