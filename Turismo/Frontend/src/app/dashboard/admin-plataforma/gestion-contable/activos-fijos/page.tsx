'use client';
import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import ActivosFijosTab from './ActivosFijosTab';
import CategoriasActivoTab from './CategoriasActivoTab';

export default function ActivosFijosPage() {
    return (
        <Tabs defaultValue="activos">
            <TabsList className="mb-4">
                <TabsTrigger value="activos">Activos Fijos</TabsTrigger>
                <TabsTrigger value="categorias">Categorías</TabsTrigger>
            </TabsList>
            <TabsContent value="activos">
                <ActivosFijosTab />
            </TabsContent>
            <TabsContent value="categorias">
                <CategoriasActivoTab />
            </TabsContent>
        </Tabs>
    );
}
