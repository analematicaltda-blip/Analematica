// frontend/src/app/dashboard/prestador/mi-negocio/gestion-contable/compras/page.tsx
'use client';
import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

import ProveedoresTab from './components/ProveedoresTab';
import FacturasCompraTab from './components/FacturasCompraTab';

export default function ComprasPage() {
  return (
    <Tabs defaultValue="facturas">
      <TabsList className="grid w-full grid-cols-2">
        <TabsTrigger value="facturas">Facturas de Compra</TabsTrigger>
        <TabsTrigger value="proveedores">Proveedores</TabsTrigger>
      </TabsList>

      <TabsContent value="facturas">
        <Card>
          <CardHeader>
            <CardTitle>Gestión de Facturas de Compra</CardTitle>
          </CardHeader>
          <CardContent>
            <FacturasCompraTab />
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="proveedores">
        <Card>
          <CardHeader>
            <CardTitle>Gestión de Proveedores</CardTitle>
          </CardHeader>
          <CardContent>
            <ProveedoresTab />
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  );
}
