"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { getFeedbackProveedor, FeedbackProveedor as Feedback } from '@/services/api';
import { FiMessageSquare, FiAlertTriangle } from 'react-icons/fi';

const FeedbackProveedor = () => {
  const [feedback, setFeedback] = useState<Feedback[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchFeedback = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getFeedbackProveedor();
      setFeedback(response.results);
    } catch (err) {
      setError('No se pudo cargar el feedback.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchFeedback();
  }, [fetchFeedback]);

  const getIconForType = (type: string) => {
    switch (type) {
      case 'SUGERENCIA': return <FiMessageSquare className="text-blue-500" />;
      case 'QUEJA': return <FiAlertTriangle className="text-red-500" />;
      default: return <FiMessageSquare />;
    }
  };

  return (
    <div className="mt-12">
      <h3 className="text-2xl font-bold text-gray-800 mb-6">Sugerencias y Quejas Recibidas</h3>
      <div className="bg-white p-6 rounded-lg shadow-md">
        {isLoading ? (
          <p className="text-center text-gray-500">Cargando feedback...</p>
        ) : error ? (
          <p className="text-center text-red-500">{error}</p>
        ) : feedback.length === 0 ? (
          <p className="text-center text-gray-500">No has recibido ninguna queja o sugerencia.</p>
        ) : (
          <div className="space-y-4">
            {feedback.map((item) => (
              <div key={item.id} className="border p-4 rounded-lg">
                <div className="flex justify-between items-start">
                    <div className="flex items-center gap-2 text-sm font-semibold">
                        <span title={item.tipo_mensaje}>{getIconForType(item.tipo_mensaje)}</span>
                        <span>{item.tipo_mensaje}</span>
                    </div>
                    <span className="text-xs text-gray-500">{new Date(item.fecha_envio).toLocaleDateString()}</span>
                </div>
                <p className="mt-2 text-gray-700">{item.mensaje}</p>
                <p className="text-right text-sm font-medium mt-2">Estado: <span className="font-bold">{item.estado}</span></p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default FeedbackProveedor;