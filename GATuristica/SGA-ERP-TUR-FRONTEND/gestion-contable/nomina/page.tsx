// frontend/src/app/dashboard/prestador/mi-negocio/gestion-contable/nomina/page.tsx
'use client';
import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import EmpleadosTab from './components/EmpleadosTab';
import PlanillasTab from './components/PlanillasTab';

export default function NominaPage() {
  return (
    <Tabs defaultValue="empleados">
      <TabsList className="grid w-full grid-cols-2">
        <TabsTrigger value="empleados">Empleados</TabsTrigger>
        <TabsTrigger value="planillas">Planillas</TabsTrigger>
      </TabsList>

      <TabsContent value="empleados">
        <Card>
          <CardHeader><CardTitle>Gestión de Empleados</CardTitle></CardHeader>
          <CardContent><EmpleadosTab /></CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="planillas">
        <Card>
          <CardHeader><CardTitle>Liquidación de Planillas</CardTitle></CardHeader>
          <CardContent><PlanillasTab /></CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  );
}
