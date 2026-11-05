// frontend/src/app/dashboard/prestador/mi-negocio/gestion-contable/inventario/page.tsx
'use client';
import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import ProductosTab from './components/ProductosTab';
import MovimientosTab from './components/MovimientosTab';

export default function InventarioPage() {
  return (
    <Tabs defaultValue="productos">
      <TabsList className="grid w-full grid-cols-2">
        <TabsTrigger value="productos">Productos</TabsTrigger>
        <TabsTrigger value="movimientos">Movimientos</TabsTrigger>
      </TabsList>

      <TabsContent value="productos">
        <Card>
          <CardHeader>
            <CardTitle>Gestión de Productos</CardTitle>
          </CardHeader>
          <CardContent>
            <ProductosTab />
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="movimientos">
        <Card>
          <CardHeader>
            <CardTitle>Movimientos de Inventario</CardTitle>
          </CardHeader>
          <CardContent>
            <MovimientosTab />
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  );
}
