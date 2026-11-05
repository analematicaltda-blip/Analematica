'use client';

import React, { useState, useEffect, Suspense, useMemo } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
    getPrestadorById, getPublicDisponibilidad, getPublicHabitaciones,
    PrestadorPublicoDetalle, Disponibilidad, Habitacion
} from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';
import Image from 'next/image';
import CalendarioReservas from '@/app/dashboard/prestador/mi-negocio/components/CalendarioReservas';
import Modal from '@/components/ui/Modal';
import { toast } from 'react-toastify';
import api from '@/lib/api';

// --- Esqueleto y componente principal ... (sin cambios) ---
function DetailPageSkeleton() { /* ... */ }

function PrestadorDetailPageContent() {
  const params = useParams();
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const id = params && params.id ? parseInt(params.id as string, 10) : null;

  const [prestador, setPrestador] = useState<PrestadorPublicoDetalle | null>(null);
  const [recursos, setRecursos] = useState<Habitacion[]>([]); // Usamos Habitacion como recurso base
  const [recursoType, setRecursoType] = useState<{appLabel: string, model: string} | null>(null);
  const [selectedRecurso, setSelectedRecurso] = useState<Habitacion | null>(null);
  const [disponibilidad, setDisponibilidad] = useState<Disponibilidad[]>([]);
  const [loading, setLoading] = useState(true);
  const [isReservaModalOpen, setIsReservaModalOpen] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState<{ start: Date, end: Date } | null>(null);

  // Cargar datos del prestador y sus recursos (habitaciones)
  useEffect(() => {
    if (id === null) return;
    const loadPrestadorYRecursos = async () => {
      try {
        setLoading(true);
        const prestadorData = await getPrestadorById(id);
        setPrestador(prestadorData);

        const categoriaSlug = prestadorData.categoria.slug;
        if (categoriaSlug.includes('hotel')) {
            const habitacionesData = await getPublicHabitaciones(prestadorData.id);
            setRecursos(habitacionesData);
            setRecursoType({ appLabel: 'turismo', model: 'habitacion' });
            if (habitacionesData.length > 0) {
                setSelectedRecurso(habitacionesData[0]);
            }
        }
        // Aquí se añadiría la lógica para otros tipos de prestadores (guías, etc.)
        // else if (categoriaSlug.includes('guia')) { ... }

      } catch (err) {
        toast.error('No se pudo cargar la información del prestador.');
      } finally {
        setLoading(false);
      }
    };
    loadPrestadorYRecursos();
  }, [id]);

  // Cargar disponibilidad cuando cambia el recurso seleccionado
  useEffect(() => {
    if (!selectedRecurso || !recursoType) return;
    const loadDisponibilidad = async () => {
        try {
            const data = await getPublicDisponibilidad(recursoType.appLabel, recursoType.model, selectedRecurso.id);
            setDisponibilidad(data);
        } catch (error) {
            toast.error("No se pudo cargar la disponibilidad para este recurso.");
        }
    };
    loadDisponibilidad();
  }, [selectedRecurso, recursoType]);

  const eventosDisponibilidad = useMemo(() => {
    return disponibilidad.map(d => ({
        title: `${d.cupos_disponibles} disponibles`,
        start: new Date(d.fecha),
        end: new Date(d.fecha),
        allDay: true,
        // Cambiar el color si no hay cupos
        backgroundColor: d.cupos_disponibles > 0 ? '#3788d8' : '#d3d3d3',
        borderColor: d.cupos_disponibles > 0 ? '#3788d8' : '#d3d3d3',
        interactive: d.cupos_disponibles > 0,
    }));
  }, [disponibilidad]);

  const [numeroPersonas, setNumeroPersonas] = useState(1);

  const handleSelectSlot = (slot: { start: Date; end: Date; }) => {
    if (!isAuthenticated) {
        toast.warn("Debes iniciar sesión para hacer una reserva.");
        router.push('/login');
        return;
    }
    setSelectedSlot(slot);
    setIsReservaModalOpen(true);
  };

  const handleConfirmReserva = async () => {
    if (!selectedSlot || !selectedRecurso || !prestador) return;

    const payload = {
      recurso_id: selectedRecurso.id,
      recurso_type: recursoType?.model, // 'habitacion', 'tour', etc.
      prestador_id: prestador.id,
      fecha_inicio: selectedSlot.start.toISOString().split('T')[0],
      fecha_fin: selectedSlot.end.toISOString().split('T')[0],
      cantidad_personas: numeroPersonas,
    };

    try {
      // Se necesitará una función `createReserva` en el servicio de API
      await api.post('/turismo/reservas/', payload);
      toast.success('¡Reserva solicitada con éxito! El prestador se pondrá en contacto contigo.');
      setIsReservaModalOpen(false);
      // Opcional: recargar disponibilidad
    } catch (error) {
      toast.error('No se pudo realizar la reserva.');
    }
  };

  if (loading) return <DetailPageSkeleton />;
  if (!prestador) return <div>Prestador no encontrado.</div>;

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'LocalBusiness',
    name: prestador.nombre_negocio,
    description: prestador.descripcion,
    image: prestador.foto_principal,
    address: {
      '@type': 'PostalAddress',
      streetAddress: prestador.direccion,
      addressLocality: prestador.municipio_nombre,
      addressCountry: 'CO'
    },
    geo: {
      '@type': 'GeoCoordinates',
      latitude: prestador.latitud,
      longitude: prestador.longitud
    },
    url: `${process.env.NEXT_PUBLIC_SITE_URL}/directorio/prestadores/${id}`,
    telephone: prestador.telefono_contacto
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
    <div className="container mx-auto px-4 py-8">
      {/* ... (encabezado, galería, etc.) ... */}

      <div className="mt-12">
        <h2 className="text-3xl font-semibold text-center mb-6">Disponibilidad y Reservas</h2>
        {/* Selector de Recurso (si hay más de uno) */}
        {recursos.length > 1 && (
            <select onChange={(e) => setSelectedRecurso(recursos.find(r => r.id === parseInt(e.target.value)) || null)}>
                {recursos.map(r => <option key={r.id} value={r.id}>{r.nombre_o_numero}</option>)}
            </select>
        )}
        <div className="max-w-4xl mx-auto bg-white p-4 rounded-lg shadow-lg">
          <CalendarioReservas eventos={eventosDisponibilidad} onSelectSlot={handleSelectSlot} onSelectEvent={() => {}} />
        </div>
      </div>

      {isReservaModalOpen && selectedSlot && (
        <Modal title="Confirmar Reserva" onClose={() => setIsReservaModalOpen(false)}>
            <div className="p-4">
                <p><strong>Recurso:</strong> {selectedRecurso?.nombre_o_numero}</p>
                <p><strong>Desde:</strong> {selectedSlot.start.toLocaleDateString()}</p>
                <p><strong>Hasta:</strong> {selectedSlot.end.toLocaleDateString()}</p>
                <div className="mt-4">
                    <label htmlFor="numero_personas">Número de Personas:</label>
                    <input
                        type="number"
                        id="numero_personas"
                        value={numeroPersonas}
                        onChange={(e) => setNumeroPersonas(parseInt(e.target.value, 10))}
                        min="1"
                        className="w-full p-2 border rounded"
                    />
                </div>
                <div className="flex justify-end mt-6 space-x-2">
                    <button onClick={() => setIsReservaModalOpen(false)} className="bg-gray-200 text-gray-800 font-bold py-2 px-4 rounded">Cancelar</button>
                    <button onClick={handleConfirmReserva} className="bg-blue-600 text-white font-bold py-2 px-4 rounded">Confirmar Solicitud</button>
                </div>
            </div>
        </Modal>
      )}
    </>
  );
}

export default function PrestadorDetailPage() {
    return (
        <Suspense fallback={<DetailPageSkeleton />}>
            <PrestadorDetailPageContent />
        </Suspense>
    )
}