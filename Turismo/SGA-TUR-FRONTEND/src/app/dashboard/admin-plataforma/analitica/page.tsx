
'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

export default function AdminAnaliticaPage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Inteligencia y Analítica del Negocio</CardTitle>
      </CardHeader>
      <CardContent>
        <p>
          Este es el dashboard de inteligencia de negocio para la plataforma Sarita.
        </p>
        <p className="mt-4 text-sm text-gray-700">
          Aquí se visualizarán los KPIs, métricas y ratios financieros para la
          toma de decisiones estratégicas.
        </p>
        <ul className="list-disc pl-5 mt-4 space-y-2 text-sm text-gray-700">
          <li>Ingresos por segmento de cliente</li>
          <li>Tasa de crecimiento de usuarios</li>
          <li>Tasa de abandono (churn) de prestadores</li>
          <li>Métricas de conversión de marketing</li>
          <li>Preparación de datos para informes fiscales</li>
        </ul>
      </CardContent>
    </Card>
  );
}
