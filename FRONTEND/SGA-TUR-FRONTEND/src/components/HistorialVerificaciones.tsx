"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { getVerificaciones, Verificacion } from '@/services/verificacionService';
import { FiEye, FiList } from 'react-icons/fi';

const HistorialVerificaciones: React.FC = () => {
    const [verificaciones, setVerificaciones] = useState<Verificacion[]>([]);
    const [selectedVerificacion, setSelectedVerificacion] = useState<Verificacion | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const loadVerificaciones = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await getVerificaciones();
            setVerificaciones(data);
        } catch (err) {
            setError("No se pudo cargar su historial. Por favor, intente más tarde.");
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        loadVerificaciones();
    }, [loadVerificaciones]);

    if (isLoading) {
        return <div className="text-center p-8">Cargando historial...</div>;
    }

    if (error) {
        return <div className="text-center p-8 text-red-500">{error}</div>;
    }

    if (selectedVerificacion) {
        return (
            <div className="p-6 bg-white rounded-lg shadow-md">
                <h2 className="text-2xl font-bold mb-4">Detalle de Verificación</h2>
                <p><strong>Plantilla:</strong> {selectedVerificacion.plantilla_nombre}</p>
                <p><strong>Fecha de Visita:</strong> {new Date(selectedVerificacion.fecha_visita).toLocaleDateString()}</p>
                <p><strong>Evaluador:</strong> {selectedVerificacion.funcionario_nombre}</p>
                <p className="text-xl mt-2"><strong>Puntaje Obtenido: <span className="font-bold text-blue-600">{selectedVerificacion.puntaje_obtenido}</span></strong></p>

                <div className="mt-4">
                    <h3 className="text-lg font-semibold">Observaciones:</h3>
                    <p className="text-gray-700 p-2 bg-gray-50 rounded">{selectedVerificacion.observaciones_generales || "Sin observaciones."}</p>
                </div>

                <div className="mt-4">
                    <h3 className="text-lg font-semibold">Recomendaciones:</h3>
                    <p className="text-gray-700 p-2 bg-gray-50 rounded">{selectedVerificacion.recomendaciones || "Sin recomendaciones."}</p>
                </div>

                <h3 className="text-xl font-semibold mt-6 mb-2">Checklist de Requisitos</h3>
                <ul className="list-disc pl-5 mt-2 space-y-2">
                    {selectedVerificacion.respuestas_items.map(item => (
                        <li key={item.id} className="flex items-center">
                           <span className={`w-5 h-5 rounded-full mr-3 ${item.cumple ? 'bg-green-500' : 'bg-red-500'}`}></span>
                           <span>{item.texto_requisito}</span>
                           <span className="ml-auto text-sm text-gray-500">{item.justificacion}</span>
                        </li>
                    ))}
                </ul>
                <button onClick={() => setSelectedVerificacion(null)} className="mt-8 bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600 flex items-center">
                    <FiList className="mr-2"/>
                    Volver al Historial
                </button>
            </div>
        );
    }

    return (
        <div className="p-6 bg-white rounded-lg shadow-md">
            <h2 className="text-2xl font-semibold text-gray-700 mb-4">Mi Historial de Verificaciones</h2>
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-100">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fecha</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Plantilla Utilizada</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Puntaje Obtenido</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {verificaciones.length > 0 ? verificaciones.map(v => (
                            <tr key={v.id}>
                                <td className="px-6 py-4 whitespace-nowrap">{new Date(v.fecha_visita).toLocaleDateString()}</td>
                                <td className="px-6 py-4 whitespace-nowrap">{v.plantilla_nombre}</td>
                                <td className="px-6 py-4 whitespace-nowrap font-bold text-lg">{v.puntaje_obtenido}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-right">
                                    <button onClick={() => setSelectedVerificacion(v)} className="text-indigo-600 hover:text-indigo-900">
                                        <FiEye className="inline mr-1" /> Ver Detalle
                                    </button>
                                </td>
                            </tr>
                        )) : (
                            <tr>
                                <td colSpan={4} className="text-center py-6 text-gray-500">Aún no tiene verificaciones registradas.</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default HistorialVerificaciones;