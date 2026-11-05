'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

export default function ReservasPage() {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Reservas Unificadas</h1>
      <Card>
        <CardHeader><CardTitle>Panel de Control de Reservas</CardTitle></CardHeader>
        <CardContent>
           <p className="text-slate-500 italic">Módulo de integración con /api/v1/turismo/tourism-reservations/</p>
        </CardContent>
      </Card>
    </div>
  );
}
