'use client';
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { AlertTriangle } from 'lucide-react';

export default function ContabilidadPlaceholderPage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <AlertTriangle className="mr-2 h-5 w-5 text-yellow-500" />
          Módulo en Construcción
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-gray-600">
          La interfaz de usuario para el módulo de Contabilidad General está planificada y se implementará en una futura fase.
        </p>
        <p className="text-gray-600 mt-2">
          Aunque el backend contable está activo y registra automáticamente los asientos de las facturas de venta, la UI para visualizar el plan de cuentas, crear asientos manuales y generar reportes aún no ha sido desarrollada.
        </p>
      </CardContent>
    </Card>
  );
}
