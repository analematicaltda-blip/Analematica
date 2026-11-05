"use client";

"use client";

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';
import { useForm, useFieldArray, useWatch, Control, UseFormRegister } from 'react-hook-form';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { FiSave, FiPlus, FiTrash2, FiArrowLeft } from 'react-icons/fi';
import { Categoria } from '@/services/api'; // Reutilizo la interfaz del servicio

// Interfaces
interface Opcion {
    id?: number;
    texto_opcion: string;
}

interface Pregunta {
    id?: number;
    texto_pregunta: string;
    tipo_pregunta: string;
    es_requerida: boolean;
    opciones: Opcion[];
}

interface FormularioData {
    titulo: string;
    descripcion: string;
    categoria: number | null;
    es_publico: boolean;
    preguntas: Pregunta[];
}

const CaracterizacionFormPage = () => {
    const { token } = useAuth();
    const router = useRouter();
    const params = useParams();
    const id = params.id as string;
    const isCreating = id === 'crear';

    const [isLoading, setIsLoading] = useState(!isCreating);
    const [categorias, setCategorias] = useState<Categoria[]>([]);

    const { register, control, handleSubmit, reset } = useForm<FormularioData>({
        defaultValues: { preguntas: [] }
    });

    const { fields, append, remove } = useFieldArray({ control, name: "preguntas" });

    const apiClient = axios.create({
        baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
        headers: { Authorization: `Token ${token}` }
    });

    // Cargar categorías para el selector
    useEffect(() => {
        apiClient.get('/prestadores/categorias/')
            .then(res => setCategorias(res.data))
            .catch(() => toast.error("No se pudieron cargar las categorías."));
    }, [apiClient]);

    // Cargar datos del formulario si estamos editando
    useEffect(() => {
        if (!isCreating && token) {
            setIsLoading(true);
            apiClient.get(`/formularios/${id}/`)
                .then(res => {
                    reset(res.data);
                })
                .catch(() => toast.error("Error al cargar el formulario."))
                .finally(() => setIsLoading(false));
        }
    }, [id, token, isCreating, reset, apiClient]);

    const onSubmit = async (data: FormularioData) => {
        const toastId = toast.loading(isCreating ? "Creando formulario..." : "Actualizando formulario...");
        try {
            const url = isCreating ? '/formularios/' : `/formularios/${id}/`;
            const method = isCreating ? 'post' : 'patch';
            await apiClient({ method, url, data });
            toast.update(toastId, { render: "Formulario guardado con éxito.", type: "success", isLoading: false, autoClose: 3000 });
            router.push('/dashboard/formularios');
        } catch {
            toast.update(toastId, { render: "Error al guardar el formulario.", type: "error", isLoading: false, autoClose: 5000 });
        }
    };

    if (isLoading) return <p>Cargando formulario...</p>;

    return (
        <div className="container mx-auto">
            <ToastContainer />
            <Link href="/dashboard/formularios" className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-6">
                <FiArrowLeft className="mr-2" /> Volver
            </Link>
            <h1 className="text-3xl font-bold text-gray-800 mb-6">
                {isCreating ? 'Crear Formulario de Caracterización' : 'Editar Formulario'}
            </h1>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
                {/* Detalles del Formulario */}
                <div className="bg-white p-6 rounded-lg shadow-md space-y-4">
                    <h2 className="text-xl font-semibold">Detalles del Formulario</h2>
                    <div>
                        <label className="block text-sm font-medium">Título</label>
                        <input {...register('titulo', { required: true })} className="mt-1 block w-full rounded-md border-gray-300"/>
                    </div>
                    <div>
                        <label className="block text-sm font-medium">Descripción</label>
                        <textarea {...register('descripcion')} rows={3} className="mt-1 block w-full rounded-md border-gray-300"/>
                    </div>
                    <div>
                        <label className="block text-sm font-medium">Asociar a Categoría</label>
                        <select {...register('categoria')} className="mt-1 block w-full rounded-md border-gray-300">
                            <option value="">Ninguna</option>
                            {categorias.map(cat => <option key={cat.id} value={cat.id}>{cat.nombre}</option>)}
                        </select>
                    </div>
                    <div className="flex items-center">
                        <input type="checkbox" {...register('es_publico')} className="h-4 w-4 rounded border-gray-300" />
                        <label className="ml-2 block text-sm">Hacer público para los prestadores</label>
                    </div>
                </div>

                {/* Preguntas */}
                <div className="bg-white p-6 rounded-lg shadow-md space-y-4">
                    <h2 className="text-xl font-semibold">Preguntas</h2>
                    {fields.map((field, index) => (
                        <PreguntaEditor key={field.id} control={control} index={index} remove={remove} register={register} />
                    ))}
                    <button type="button" onClick={() => append({ texto_pregunta: '', tipo_pregunta: 'TEXTO_CORTO', es_requerida: false, opciones: [] })}
                        className="inline-flex items-center px-4 py-2 border border-dashed text-sm font-medium rounded-md text-blue-700 hover:bg-blue-50">
                        <FiPlus className="mr-2"/> Añadir Pregunta
                    </button>
                </div>

                <div className="flex justify-end">
                    <button type="submit" className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-bold rounded-lg shadow-md hover:bg-blue-700">
                        <FiSave className="mr-2"/> Guardar Formulario
                    </button>
                </div>
            </form>
        </div>
    );
};

interface PreguntaEditorProps {
    control: Control<FormularioData>;
    index: number;
    remove: (index: number) => void;
    register: UseFormRegister<FormularioData>;
}

// Componente anidado para editar una pregunta y sus opciones
const PreguntaEditor = ({ control, index, remove, register }: PreguntaEditorProps) => {
    const { fields: opciones, append, remove: removeOpcion } = useFieldArray({ control, name: `preguntas.${index}.opciones` });
    const tipoPregunta = useWatch({ control, name: `preguntas.${index}.tipo_pregunta` });

    return (
        <div className="border p-4 rounded-lg space-y-3 bg-gray-50">
            <div className="flex justify-between items-start">
                <div className="flex-grow">
                    <label className="block text-sm font-medium">Texto de la Pregunta</label>
                    <input {...register(`preguntas.${index}.texto_pregunta`, { required: true })} className="mt-1 block w-full rounded-md border-gray-300"/>
                </div>
                <button type="button" onClick={() => remove(index)} className="ml-4 text-red-500 hover:text-red-700"><FiTrash2/></button>
            </div>
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <label className="block text-sm font-medium">Tipo de Pregunta</label>
                    <select {...register(`preguntas.${index}.tipo_pregunta`)} className="mt-1 block w-full rounded-md border-gray-300">
                        <option value="TEXTO_CORTO">Texto Corto</option>
                        <option value="TEXTO_LARGO">Texto Largo</option>
                        <option value="NUMERO">Número</option>
                        <option value="FECHA">Fecha</option>
                        <option value="SELECCION_UNICA">Selección Única</option>
                        <option value="SELECCION_MULTIPLE">Selección Múltiple</option>
                    </select>
                </div>
                <div className="flex items-end">
                    <input type="checkbox" {...register(`preguntas.${index}.es_requerida`)} className="h-4 w-4 rounded border-gray-300" />
                    <label className="ml-2 block text-sm">Es requerida</label>
                </div>
            </div>

            {['SELECCION_UNICA', 'SELECCION_MULTIPLE'].includes(tipoPregunta) && (
                <div className="pl-4 border-l-2 space-y-2">
                    <h4 className="text-sm font-semibold">Opciones de Respuesta</h4>
                    {opciones.map((opcion, opcIndex) => (
                        <div key={opcion.id} className="flex items-center space-x-2">
                            <input {...register(`preguntas.${index}.opciones.${opcIndex}.texto_opcion`, { required: true })} className="flex-grow rounded-md border-gray-300 text-sm"/>
                            <button type="button" onClick={() => removeOpcion(opcIndex)} className="text-red-400 hover:text-red-600"><FiTrash2 size={16}/></button>
                        </div>
                    ))}
                     <button type="button" onClick={() => append({ texto_opcion: '' })}
                        className="text-xs inline-flex items-center px-2 py-1 border border-dashed rounded text-blue-600 hover:bg-blue-50">
                        <FiPlus className="mr-1"/> Añadir Opción
                    </button>
                </div>
            )}
        </div>
    );
};

export default CaracterizacionFormPage;