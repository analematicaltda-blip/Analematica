"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { getCapacitacionDetalle, registrarAsistencia, Capacitacion } from '@/services/capacitacionService';
import { getUsuariosAdmin, UsuarioAdmin } from '@/services/adminService';
import { useForm, SubmitHandler } from 'react-hook-form';
import { FiUsers, FiSave, FiArrowLeft } from 'react-icons/fi';

interface CapacitacionDetailProps {
    capacitacionId: number;
    onBack: () => void;
}

interface FormValues {
    asistentes: Record<string, boolean>;
}

const CapacitacionDetail: React.FC<CapacitacionDetailProps> = ({ capacitacionId, onBack }) => {
    const [capacitacion, setCapacitacion] = useState<Capacitacion | null>(null);
    const [usuarios, setUsuarios] = useState<UsuarioAdmin[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const { register, handleSubmit, reset } = useForm<FormValues>();

    const loadData = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const [capacitacionData, usuariosData] = await Promise.all([
                getCapacitacionDetalle(capacitacionId),
                getUsuariosAdmin()
            ]);
            setCapacitacion(capacitacionData);
            setUsuarios(usuariosData);

            // Inicializar el formulario con los asistentes actuales
            const initialAsistentes: Record<string, boolean> = {};
            usuariosData.forEach(u => {
                initialAsistentes[u.id] = capacitacionData.asistentes.some(a => a.usuario === u.id);
            });
            reset({ asistentes: initialAsistentes });

        } catch (err) {
            setError("No se pudieron cargar los detalles de la capacitación.");
        } finally {
            setIsLoading(false);
        }
    }, [capacitacionId, reset]);

    useEffect(() => {
        loadData();
    }, [loadData]);

    const onSubmit: SubmitHandler<FormValues> = async (data) => {
        setIsSubmitting(true);
        setError(null);
        try {
            const asistentesIds = Object.keys(data.asistentes).filter(id => data.asistentes[id]);
            await registrarAsistencia(capacitacionId, asistentesIds.map(Number));
            alert('Asistencia registrada con éxito. Los puntajes han sido actualizados.');
            onBack(); // Volver a la lista
        } catch (err) {
            setError("No se pudo guardar la asistencia.");
        } finally {
            setIsSubmitting(false);
        }
    };

    if (isLoading) {
        return <div className="text-center p-8">Cargando detalles de la capacitación...</div>;
    }

    if (error) {
        return <div className="text-center p-8 text-red-500">{error}</div>;
    }

    if (!capacitacion) {
        return <div className="text-center p-8">No se encontró la capacitación.</div>;
    }

    return (
        <div className="p-6 bg-white rounded-lg shadow-md">
            <button onClick={onBack} className="flex items-center text-blue-600 hover:underline mb-4">
                <FiArrowLeft className="mr-2" /> Volver a la lista
            </button>
            <h1 className="text-2xl font-bold text-gray-800">{capacitacion.titulo}</h1>
            <p className="text-gray-600">Puntos por asistencia: <span className="font-bold">{capacitacion.puntos_asistencia}</span></p>

            <form onSubmit={handleSubmit(onSubmit)} className="mt-6">
                <h2 className="text-xl font-semibold text-gray-700 mb-4 flex items-center">
                    <FiUsers className="mr-2" /> Registrar Asistencia
                </h2>

                <div className="max-h-96 overflow-y-auto border rounded-lg p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {usuarios.map(usuario => (
                        <div key={usuario.id} className="flex items-center p-2 bg-gray-50 rounded">
                            <input
                                type="checkbox"
                                id={`user-${usuario.id}`}
                                {...register(`asistentes.${usuario.id}`)}
                                className="h-5 w-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                            />
                            <label htmlFor={`user-${usuario.id}`} className="ml-3 text-sm text-gray-700">
                                {usuario.nombre_display} <span className="text-xs text-gray-500">({usuario.rol_display})</span>
                            </label>
                        </div>
                    ))}
                </div>

                {error && <p className="text-red-500 mt-4">{error}</p>}

                <div className="mt-6 flex justify-end">
                    <button
                        type="submit"
                        disabled={isSubmitting}
                        className="bg-green-600 text-white py-2 px-6 rounded-md hover:bg-green-700 disabled:bg-green-300 flex items-center"
                    >
                        <FiSave className="mr-2" />
                        {isSubmitting ? "Guardando..." : "Guardar Asistencia"}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default CapacitacionDetail;