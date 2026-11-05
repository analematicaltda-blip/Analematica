"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { getPlantillas, getVerificaciones, iniciarVerificacion, Verificacion, PlantillaVerificacion } from '@/services/verificacionService';
import { getPrestadoresAdmin } from '@/services/adminService';
import FormularioVerificacion from './FormularioVerificacion'; // Se creará a continuación
import { FiPlusCircle, FiEye } from 'react-icons/fi';

// Interfaz simplificada para el prestador en el selector
interface PrestadorInfo {
    id: number;
    nombre_negocio: string;
}

const VerificacionManager: React.FC = () => {
    const [view, setView] = useState<'list' | 'form' | 'detail'>('list');
    const [verificaciones, setVerificaciones] = useState<Verificacion[]>([]);
    const [plantillas, setPlantillas] = useState<PlantillaVerificacion[]>([]);
    const [prestadores, setPrestadores] = useState<PrestadorInfo[]>([]);
    const [activeVerificacion, setActiveVerificacion] = useState<Verificacion | null>(null);

    const [selectedPlantilla, setSelectedPlantilla] = useState<string>('');
    const [selectedPrestador, setSelectedPrestador] = useState<string>('');

    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const loadInitialData = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const [verificacionesData, plantillasData, prestadoresData] = await Promise.all([
                getVerificaciones(),
                getPlantillas(),
                getPrestadoresAdmin()
            ]);
            setVerificaciones(verificacionesData);
            setPlantillas(plantillasData);
            setPrestadores(prestadoresData.map(p => ({ id: p.id, nombre_negocio: p.nombre_negocio })));
        } catch (err) {
            setError("No se pudieron cargar los datos. Por favor, intente de nuevo más tarde.");
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        loadInitialData();
    }, [loadInitialData]);

    const handleIniciarVerificacion = async () => {
        if (!selectedPlantilla || !selectedPrestador) {
            setError("Por favor, seleccione una plantilla y un prestador.");
            return;
        }
        setIsSubmitting(true);
        setError(null);
        try {
            const nuevaVerificacion = await iniciarVerificacion(Number(selectedPlantilla), Number(selectedPrestador));
            setActiveVerificacion(nuevaVerificacion);
            setView('form');
        } catch (err) {
            setError("No se pudo iniciar la verificación. Verifique los datos e intente de nuevo.");
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleFormSuccess = () => {
        setView('list');
        setActiveVerificacion(null);
        loadInitialData(); // Recargar la lista de verificaciones
    };

    const handleCancel = () => {
        setView('list');
        setActiveVerificacion(null);
    };

    const handleViewDetail = (verificacion: Verificacion) => {
        setActiveVerificacion(verificacion);
        setView('detail');
    };

    if (isLoading) {
        return <div className="text-center p-8">Cargando gestor de verificaciones...</div>;
    }

    if (error && view === 'list') {
        return <div className="text-center p-8 text-red-500">{error}</div>;
    }

    if (view === 'form' && activeVerificacion) {
        return (
            <FormularioVerificacion
                verificacionInicial={activeVerificacion}
                onSuccess={handleFormSuccess}
                onCancel={handleCancel}
            />
        );
    }

    if (view === 'detail' && activeVerificacion) {
        // Vista de detalle simple (podría ser un componente separado)
        return (
            <div className="p-6 bg-white rounded-lg shadow-md">
                <h2 className="text-2xl font-bold mb-4">Detalle de Verificación</h2>
                <p><strong>Prestador:</strong> {activeVerificacion.prestador_nombre}</p>
                <p><strong>Plantilla:</strong> {activeVerificacion.plantilla_nombre}</p>
                <p><strong>Fecha:</strong> {new Date(activeVerificacion.fecha_visita).toLocaleDateString()}</p>
                <p><strong>Puntaje Obtenido:</strong> {activeVerificacion.puntaje_obtenido}</p>
                <h3 className="text-xl font-semibold mt-4">Respuestas</h3>
                <ul className="list-disc pl-5 mt-2">
                    {activeVerificacion.respuestas_items.map(item => (
                        <li key={item.id} className={item.cumple ? 'text-green-600' : 'text-red-600'}>
                           {item.texto_requisito}: {item.cumple ? 'Sí' : 'No'}
                        </li>
                    ))}
                </ul>
                <button onClick={handleCancel} className="mt-6 bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600">
                    Volver a la lista
                </button>
            </div>
        );
    }

    return (
        <div className="p-6 bg-gray-50 min-h-screen">
            <h1 className="text-3xl font-bold text-gray-800 mb-6">Gestor de Verificación de Cumplimiento</h1>

            {/* Sección para Iniciar Nueva Verificación */}
            <div className="bg-white p-6 rounded-lg shadow-md mb-8">
                <h2 className="text-2xl font-semibold text-gray-700 mb-4 flex items-center">
                    <FiPlusCircle className="mr-2 text-blue-500" />
                    Iniciar Nueva Verificación
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <select
                        value={selectedPlantilla}
                        onChange={(e) => setSelectedPlantilla(e.target.value)}
                        className="w-full p-2 border border-gray-300 rounded-md"
                    >
                        <option value="">-- Seleccione una Plantilla --</option>
                        {plantillas.map(p => <option key={p.id} value={p.id}>{p.nombre}</option>)}
                    </select>
                    <select
                        value={selectedPrestador}
                        onChange={(e) => setSelectedPrestador(e.target.value)}
                        className="w-full p-2 border border-gray-300 rounded-md"
                    >
                        <option value="">-- Seleccione un Prestador --</option>
                        {prestadores.map(p => <option key={p.id} value={p.id}>{p.nombre_negocio}</option>)}
                    </select>
                    <button
                        onClick={handleIniciarVerificacion}
                        disabled={isSubmitting || !selectedPlantilla || !selectedPrestador}
                        className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-blue-300"
                    >
                        {isSubmitting ? "Iniciando..." : "Iniciar"}
                    </button>
                </div>
                {error && <p className="text-red-500 mt-2">{error}</p>}
            </div>

            {/* Sección de Verificaciones Realizadas */}
            <div className="bg-white p-6 rounded-lg shadow-md">
                <h2 className="text-2xl font-semibold text-gray-700 mb-4">Historial de Verificaciones</h2>
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-100">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fecha</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Prestador</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Plantilla</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Puntaje</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {verificaciones.length > 0 ? verificaciones.map(v => (
                                <tr key={v.id}>
                                    <td className="px-6 py-4 whitespace-nowrap">{new Date(v.fecha_visita).toLocaleDateString()}</td>
                                    <td className="px-6 py-4 whitespace-nowrap">{v.prestador_nombre}</td>
                                    <td className="px-6 py-4 whitespace-nowrap">{v.plantilla_nombre}</td>
                                    <td className="px-6 py-4 whitespace-nowrap font-bold">{v.puntaje_obtenido}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right">
                                        <button onClick={() => handleViewDetail(v)} className="text-indigo-600 hover:text-indigo-900">
                                            <FiEye className="inline mr-1" /> Ver Detalle
                                        </button>
                                    </td>
                                </tr>
                            )) : (
                                <tr>
                                    <td colSpan={5} className="text-center py-4">No se han realizado verificaciones.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default VerificacionManager;