'use client';
import React, { useState } from 'react';
import { useContabilidadApi } from '@/app/dashboard/prestador/mi-negocio/hooks/useContabilidadApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { PlusCircle } from 'lucide-react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { format } from 'date-fns';

const ContabilidadPage = () => {
    const {
        costCenters,
        costCentersLoading,
        journalEntries,
        journalEntriesLoading,
    } = useContabilidadApi();

    // TODO: Implementar modales para crear/editar/eliminar
    // TODO: Implementar paginación si es necesario

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4">Módulo de Contabilidad</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Sección de Centros de Costo */}
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between">
                        <CardTitle>Centros de Costo</CardTitle>
                        <Button size="sm">
                            <PlusCircle className="mr-2 h-4 w-4" /> Nuevo
                        </Button>
                    </CardHeader>
                    <CardContent>
                        {costCentersLoading && <p>Cargando centros de costo...</p>}
                        {!costCentersLoading && costCenters && (
                             <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Código</TableHead>
                                        <TableHead>Nombre</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {costCenters.results.map((center: any) => (
                                        <TableRow key={center.id}>
                                            <TableCell>{center.code}</TableCell>
                                            <TableCell>{center.name}</TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        )}
                         {!costCentersLoading && (!costCenters || costCenters.results.length === 0) && (
                            <p className="text-center text-gray-500">No hay centros de costo.</p>
                        )}
                    </CardContent>
                </Card>

                {/* Sección de Asientos Contables */}
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between">
                        <CardTitle>Asientos Contables</CardTitle>
                         <Button size="sm">
                            <PlusCircle className="mr-2 h-4 w-4" /> Nuevo Asiento
                        </Button>
                    </CardHeader>
                    <CardContent>
                        {journalEntriesLoading && <p>Cargando asientos...</p>}
                        {!journalEntriesLoading && journalEntries && (
                             <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Fecha</TableHead>
                                        <TableHead>Descripción</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {journalEntries.results.map((entry: any) => (
                                        <TableRow key={entry.id}>
                                            <TableCell>{format(new Date(entry.entry_date), 'dd/MM/yyyy')}</TableCell>
                                            <TableCell>{entry.description}</TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        )}
                         {!journalEntriesLoading && (!journalEntries || journalEntries.results.length === 0) && (
                            <p className="text-center text-gray-500">No hay asientos contables.</p>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default ContabilidadPage;
