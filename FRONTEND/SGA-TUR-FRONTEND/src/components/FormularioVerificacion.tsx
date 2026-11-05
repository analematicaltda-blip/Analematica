"use client";

import React, { useState } from 'react';
import { useForm, useFieldArray, SubmitHandler, Controller } from 'react-hook-form';
import { Verificacion, GuardarVerificacionPayload, guardarVerificacion } from '@/services/verificacionService';

interface FormularioVerificacionProps {
    verificacionInicial: Verificacion;
    onSuccess: () => void;
    onCancel: () => void;
}

const FormularioVerificacion: React.FC<FormularioVerificacionProps> = ({ verificacionInicial, onSuccess, onCancel }) => {
    const { register, control, handleSubmit, formState: { errors } } = useForm<Verificacion>({
        defaultValues: {
            ...verificacionInicial,
            // Asegurarse de que la fecha esté en formato YYYY-MM-DD para el input
            fecha_visita: new Date(verificacionInicial.fecha_visita).toISOString().split('T')[0],
        },
    });

    const { fields } = useFieldArray({
        control,
        name: "respuestas_items",
    });

    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const onSubmit: SubmitHandler<Verificacion> = async (data) => {
        setIsSubmitting(true);
        setError(null);

        // Transformar los datos del formulario al payload que espera la API
        const payload: GuardarVerificacionPayload = {
            fecha_visita: data.fecha_visita,
            observaciones_generales: data.observaciones_generales,
            recomendaciones: data.recomendaciones,
            respuestas_items: data.respuestas_items.map(item => ({
                item_original_id: item.item_original_id,
                cumple: item.cumple,
                justificacion: item.justificacion,
            })),
        };

        try {
            await guardarVerificacion(verificacionInicial.id, payload);
            alert('Verificación guardada con éxito. El puntaje del prestador ha sido actualizado.');
            onSuccess();
        } catch (err) {
            setError("Ocurrió un error al guardar la verificación. Por favor, intente de nuevo.");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="p-8 bg-white rounded-lg shadow-xl max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold text-gray-800">Formato de Verificación</h1>
            <p className="text-lg text-gray-600 mt-1">Plantilla: <span className="font-semibold">{verificacionInicial.plantilla_nombre}</span></p>
            <p className="text-lg text-gray-600">Prestador: <span className="font-semibold">{verificacionInicial.prestador_nombre}</span></p>

            <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-6">

                {/* --- Datos Generales de la Visita --- */}
                <div className="p-4 border rounded-md">
                    <h2 className="text-xl font-semibold text-gray-700 mb-4">Datos de la Visita</h2>
                     <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label htmlFor="fecha_visita" className="block text-sm font-medium text-gray-700">Fecha de la Visita</label>
                            <input
                                type="date"
                                id="fecha_visita"
                                {...register('fecha_visita', { required: "La fecha es obligatoria" })}
                                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                            />
                            {errors.fecha_visita && <p className="text-red-500 text-xs mt-1">{errors.fecha_visita.message}</p>}
                        </div>
                    </div>
                </div>

                {/* --- Checklist de Requisitos --- */}
                <div>
                    <h2 className="text-xl font-semibold text-gray-700 mb-4">Lista de Chequeo de Requisitos</h2>
                    <div className="overflow-x-auto border rounded-md">
                        <table className="min-w-full">
                            <thead className="bg-gray-100">
                                <tr>
                                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Requisito</th>
                                    <th className="px-2 py-3 text-center text-sm font-semibold text-gray-600">Puntaje</th>
                                    <th className="px-4 py-3 text-center text-sm font-semibold text-gray-600">¿Cumple?</th>
                                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Justificación / Soporte</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {fields.map((item, index) => (
                                    <tr key={item.id}>
                                        <td className="px-4 py-3 text-sm text-gray-800">{item.texto_requisito}</td>
                                        <td className="px-2 py-3 text-center text-sm font-mono">{item.puntaje}</td>
                                        <td className="px-4 py-3 text-center">
                                            <input
                                                type="checkbox"
                                                {...register(`respuestas_items.${index}.cumple`)}
                                                className="h-5 w-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                                            />
                                        </td>
                                        <td className="px-4 py-3">
                                            <input
                                                type="text"
                                                {...register(`respuestas_items.${index}.justificacion`)}
                                                placeholder="Ej: Resolución N° 123, o justificación"
                                                className="w-full px-2 py-1 border border-gray-300 rounded-md text-sm"
                                            />
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* --- Observaciones y Recomendaciones --- */}
                <div className="space-y-4">
                    <div>
                        <label htmlFor="observaciones_generales" className="block text-sm font-medium text-gray-700">Observaciones Generales</label>
                        <textarea
                            id="observaciones_generales"
                            {...register('observaciones_generales')}
                            rows={4}
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                        ></textarea>
                    </div>
                    <div>
                        <label htmlFor="recomendaciones" className="block text-sm font-medium text-gray-700">Recomendaciones para el Prestador</label>
                        <textarea
                            id="recomendaciones"
                            {...register('recomendaciones')}
                            rows={4}
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                        ></textarea>
                    </div>
                </div>

                {error && <p className="text-red-500 text-sm font-semibold">{error}</p>}

                {/* --- Botones de Acción --- */}
                <div className="flex justify-end space-x-4 pt-4">
                    <button
                        type="button"
                        onClick={onCancel}
                        className="bg-gray-200 text-gray-700 py-2 px-6 rounded-md hover:bg-gray-300 transition-colors"
                    >
                        Cancelar
                    </button>
                    <button
                        type="submit"
                        disabled={isSubmitting}
                        className="bg-green-600 text-white py-2 px-6 rounded-md hover:bg-green-700 disabled:bg-green-300 transition-colors"
                    >
                        {isSubmitting ? 'Guardando...' : 'Guardar Verificación'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default FormularioVerificacion;