'use client';

import React from 'react';
import { Calendar, momentLocalizer, EventProps } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { withDragAndDrop, DragAndDropProps } from 'react-big-calendar/lib/addons/dragAndDrop';
import 'react-big-calendar/lib/addons/dragAndDrop/styles.css';

// Configurar el localizador para moment.js
const localizer = momentLocalizer(moment);
const DnDCalendar = withDragAndDrop(Calendar as React.ComponentType<CalendarProps & DragAndDropProps<any, object>>);

// Tipado para los eventos del calendario
export interface EventoCalendario {
  id: number;
  title: string;
  start: Date;
  end: Date;
  allDay?: boolean;
  resource?: any;
  estado?: string; // Añadir estado para colorear
}

interface CalendarioReservasProps {
  eventos: EventoCalendario[];
  onSelectSlot: (slotInfo: { start: Date; end: Date; }) => void;
  onSelectEvent: (event: EventoCalendario) => void;
  onEventDrop: (data: any) => void;
}

const eventStyleGetter = (event: EventoCalendario) => {
    let backgroundColor = '#3174ad'; // Azul por defecto (Confirmada)
    switch(event.estado) {
        case 'PENDIENTE': backgroundColor = '#f0ad4e'; break; // Amarillo
        case 'CANCELADA': backgroundColor = '#d9534f'; break; // Rojo
        case 'COMPLETADA': backgroundColor = '#5cb85c'; break; // Verde
    }
    return { style: { backgroundColor } };
};

const CalendarioReservas: React.FC<CalendarioReservasProps> = ({ eventos, onSelectSlot, onSelectEvent, onEventDrop }) => {
  return (
    <div style={{ height: 600 }}>
      <DnDCalendar
        localizer={localizer}
        events={eventos}
        startAccessor="start"
        endAccessor="end"
        style={{ height: '100%' }}
        selectable
        onSelectSlot={onSelectSlot}
        onSelectEvent={onSelectEvent}
        onEventDrop={onEventDrop}
        eventPropGetter={eventStyleGetter}
        messages={{
            next: "Sig",
            previous: "Ant",
            today: "Hoy",
            month: "Mes",
            week: "Semana",
            day: "Día"
        }}
      />
    </div>
  );
};

export default CalendarioReservas;