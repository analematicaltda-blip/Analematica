"use client";

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface Contenido {
  id: number;
  seccion: string;
  titulo: string;
  contenido: string;
  orden: number;
}

const SECCION_LABELS: { [key: string]: string } = {
    INTRODUCCION: "Introducción General",
    UBICACION_CLIMA: "Ubicación y Clima",
    ALOJAMIENTO: "Alojamiento y Hotelería",
    COMO_LLEGAR: "Cómo Llegar",
    CONTACTOS: "Contactos de Interés",
    FINANZAS: "Entidades Financieras",
    OTRA: "Información Adicional",
};

export default function InformacionGeneralPage() {
  const [contenidos, setContenidos] = useState<Contenido[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchContenidos = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/contenido-municipio/`);
      setContenidos(response.data.results);
    } catch (err) {
      setError('No se pudo cargar la información del municipio. Por favor, inténtelo de nuevo más tarde.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchContenidos();
  }, [fetchContenidos]);

  // Agrupar contenidos por sección para renderizarlos
  const groupedContent = contenidos.reduce((acc, item) => {
    (acc[item.seccion] = acc[item.seccion] || []).push(item);
    return acc;
  }, {} as Record<string, Contenido[]>);

  if (isLoading) return <p className="text-center py-10">Cargando información...</p>;
  if (error) return <p className="text-center text-red-500 py-10">{error}</p>;

  return (
    <div className="container mx-auto px-4 py-12">
      <h1 className="text-5xl font-extrabold text-center mb-12 text-gray-800">
        Conoce Puerto Gaitán
      </h1>

      {Object.entries(groupedContent).map(([seccion, items]) => (
        <section key={seccion} className="mb-16">
          <h2 className="text-3xl font-bold border-b-4 border-amber-500 pb-2 mb-8">
            {SECCION_LABELS[seccion] || 'Información Adicional'}
          </h2>
          <div className="space-y-8">
            {items.map(item => (
              <div key={item.id} className="bg-white p-6 rounded-lg shadow-lg">
                <h3 className="text-2xl font-semibold mb-3">{item.titulo}</h3>
                {/* El contenido se renderiza como texto plano. Para Markdown, se necesitaría un parser. */}
                <div className="prose max-w-none text-gray-700 whitespace-pre-wrap">
                  {item.contenido}
                </div>
              </div>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}