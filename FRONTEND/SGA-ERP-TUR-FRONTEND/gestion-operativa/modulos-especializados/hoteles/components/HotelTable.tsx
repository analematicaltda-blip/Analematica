'use client';

import React from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { Room } from '../types/hotel.types';

export const HotelTable = ({ rooms }: { rooms: Room[] }) => {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>N° Habitación</TableHead>
          <TableHead>Tipo</TableHead>
          <TableHead>Estado</TableHead>
          <TableHead>Limpieza</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rooms.map((room) => (
          <TableRow key={room.id}>
            <TableCell className="font-bold">{room.room_number}</TableCell>
            <TableCell>{room.room_type.name}</TableCell>
            <TableCell>
              <Badge className={room.status === 'AVAILABLE' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}>
                {room.status}
              </Badge>
            </TableCell>
            <TableCell>
              <Badge variant="outline">{room.housekeeping_status}</Badge>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};
