'use client';
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { AlertTriangle } from 'lucide-react';

export default function ProductosServiciosPlaceholderPage() {
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
          La funcionalidad para la gestión de Productos y Servicios está planificada y se implementará en una futura fase.
        </p>
        <p className="text-gray-600 mt-2">
          Actualmente, los productos se pueden gestionar indirectamente al crear una factura de venta, pero este módulo proporcionará una interfaz dedicada para el CRUD completo.
        </p>
      </CardContent>
    </Card>
  );
}
