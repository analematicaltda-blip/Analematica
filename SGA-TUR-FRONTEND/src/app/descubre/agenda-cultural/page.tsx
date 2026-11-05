"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Calendar, momentLocalizer, Views, EventProps } from 'react-big-calendar';
import moment from 'moment';
import 'moment/locale/es'; // Localización en español para moment
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { getPublicaciones, Publicacion } from '@/services/api';
import Link from 'next/link';
import PlaceholderContent from '@/components/common/PlaceholderContent';

// Configurar moment en español
moment.locale('es');

// Localizador para react-big-calendar
const localizer = momentLocalizer(moment);

// Tipo de evento del calendario
interface CalendarEvent {
  id: number;
  title: string;
  start: Date;
  end: Date;
  resource: Publicacion; // Guardamos el evento original para más detalles
}

// Componente personalizado para renderizar cada evento
const CustomEvent = ({ event }: EventProps<CalendarEvent>) => (
  <Link href={`/publicaciones/${event.resource.slug}`}>
    <div className="p-1 h-full rounded-md hover:bg-blue-700 transition-colors duration-200">
      <strong className="block truncate">{event.title}</strong>
    </div>
  </Link>
);

export default function AgendaCulturalPage() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Cargar eventos según rango visible
  const fetchEvents = useCallback(async (range: { start: Date; end: Date }) => {
    setError(null);
    try {
      const publications = await getPublicaciones({
        tipo: 'EVENTO',
        start_date: range.start.toISOString(),
        end_date: range.end.toISOString(),
      });

      const calendarEvents = publications.map((pub) => ({
        id: pub.id,
        title: pub.titulo,
        start: new Date(pub.fecha_evento_inicio || pub.fecha_publicacion),
        end: new Date(pub.fecha_evento_fin || pub.fecha_evento_inicio || pub.fecha_publicacion),
        resource: pub,
      }));

      setEvents(calendarEvents);
    } catch (err) {
      setError('No se pudieron cargar los eventos del calendario.');
    }
  }, []);

  // Se dispara al cambiar rango o vista
  const handleRangeChange = useCallback(
    (range: Date[] | { start: Date; end: Date }) => {
      let start: Date, end: Date;
      if (Array.isArray(range)) {
        // Vista "Mes" devuelve un array de días
        start = moment(range[0]).startOf('week').toDate();
        end = moment(range[range.length - 1]).endOf('week').toDate();
      } else {
        // Semana / Día devuelven objeto con { start, end }
        start = range.start;
        end = range.end;
      }
      fetchEvents({ start, end });
    },
    [fetchEvents]
  );

  // Carga inicial
  useEffect(() => {
    const today = new Date();
    const start = moment(today).startOf('month').startOf('week').toDate();
    const end = moment(today).endOf('month').endOf('week').toDate();
    fetchEvents({ start, end });
  }, [fetchEvents]);

  // Mostrar placeholder si no hay eventos ni errores
  if (!error && events.length === 0) {
    return (
      <PlaceholderContent
        title="Agenda Cultural"
        description="Próximamente aquí encontrarás un calendario detallado de actividades, con opciones de inscripción y exportación."
      />
    );
  }

  return (
    <div className="bg-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl">
            Agenda Cultural y de Eventos
          </h1>
          <p className="mt-4 text-xl text-gray-600">
            Explora todos los eventos culturales, cívicos y deportivos.
          </p>
        </div>

        {error && (
          <div className="text-center text-red-500 bg-red-100 p-4 rounded-lg mb-8">
            <p>{error}</p>
          </div>
        )}

        {events.length > 0 && (
          <div className="h-[70vh] bg-white p-4 rounded-lg shadow-lg">
            <Calendar
              localizer={localizer}
              events={events}
              startAccessor="start"
              endAccessor="end"
              views={[Views.MONTH, Views.WEEK, Views.DAY, Views.AGENDA]}
              onRangeChange={handleRangeChange}
              components={{
                event: CustomEvent,
              }}
              messages={{
                next: 'Siguiente',
                previous: 'Anterior',
                today: 'Hoy',
                month: 'Mes',
                week: 'Semana',
                day: 'Día',
                agenda: 'Agenda',
                date: 'Fecha',
                time: 'Hora',
                event: 'Evento',
                noEventsInRange: 'No hay eventos en este rango.',
              }}
              eventPropGetter={() => ({
                className: `bg-blue-500 text-white border-none rounded-md`,
              })}
            />
          </div>
        )}
      </div>
    </div>
  );
}
