"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { getCapacitaciones } from '@/services/capacitacionService';
import { Publicacion } from '@/services/publicacionService'; // Asumiendo interfaz base
import CapacitacionDetail from './CapacitacionDetail'; // Se creará a continuación
import { FiCalendar, FiEdit } from 'react-icons/fi';

const CapacitacionesManager: React.FC = () => {
    const [capacitaciones, setCapacitaciones] = useState<Publicacion[]>([]);
    const [selectedCapacitacion, setSelectedCapacitacion] = useState<Publicacion | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const loadCapacitaciones = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await getCapacitaciones();
            setCapacitaciones(data);
        } catch (err) {
            setError("No se pudieron cargar las capacitaciones.");
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        loadCapacitaciones();
    }, [loadCapacitaciones]);

    const handleSelectCapacitacion = (capacitacion: Publicacion) => {
        setSelectedCapacitacion(capacitacion);
    };

    const handleBackToList = () => {
        setSelectedCapacitacion(null);
        loadCapacitaciones(); // Recargar por si hubo cambios
    };

    if (isLoading) {
        return <div className="text-center p-8">Cargando capacitaciones...</div>;
    }

    if (error) {
        return <div className="text-center p-8 text-red-500">{error}</div>;
    }

    if (selectedCapacitacion) {
        return <CapacitacionDetail capacitacionId={selectedCapacitacion.id!} onBack={handleBackToList} />;
    }

    return (
        <div className="p-6 bg-white rounded-lg shadow-md">
            <h1 className="text-2xl font-bold text-gray-800 mb-6">Gestor de Capacitaciones</h1>
            <div className="space-y-4">
                {capacitaciones.length > 0 ? capacitaciones.map(cap => (
                    <div key={cap.id} className="p-4 border rounded-lg flex justify-between items-center">
                        <div>
                            <h2 className="text-lg font-semibold text-gray-700">{cap.titulo}</h2>
                            <p className="text-sm text-gray-500 flex items-center mt-1">
                                <FiCalendar className="mr-2" />
                                {new Date(cap.fecha_evento_inicio!).toLocaleDateString()}
                            </p>
                        </div>
                        <button
                            onClick={() => handleSelectCapacitacion(cap)}
                            className="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 flex items-center"
                        >
                            <FiEdit className="mr-2" />
                            Gestionar Asistencia
                        </button>
                    </div>
                )) : (
                    <p className="text-center text-gray-500 py-8">No hay capacitaciones para mostrar.</p>
                )}
            </div>
        </div>
    );
};

export default CapacitacionesManager;