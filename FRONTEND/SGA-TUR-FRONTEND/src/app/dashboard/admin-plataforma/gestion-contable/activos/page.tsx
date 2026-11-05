'use client';
import React from 'react';
import { useActivosApi } from '@/app/dashboard/prestador/mi-negocio/hooks/useActivosApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { PlusCircle, Archive } from 'lucide-react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { format } from 'date-fns';

const ActivosPage = () => {
    const {
        activos,
        activosLoading,
        depreciaciones,
        depreciacionesLoading,
    } = useActivosApi();

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4 flex items-center">
                <Archive className="mr-2" /> Módulo de Activos Fijos
            </h1>

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                {/* Sección de Activos Fijos */}
                <Card className="xl:col-span-2">
                    <CardHeader className="flex flex-row items-center justify-between">
                        <CardTitle>Activos Fijos Registrados</CardTitle>
                        <Button size="sm">
                            <PlusCircle className="mr-2 h-4 w-4" /> Nuevo Activo
                        </Button>
                    </CardHeader>
                    <CardContent>
                        {activosLoading && <p>Cargando activos...</p>}
                        {!activosLoading && activos && (
                             <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Activo</TableHead>
                                        <TableHead>Categoría</TableHead>
                                        <TableHead>Valor Adquisición</TableHead>
                                        <TableHead>Valor en Libros</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {activos.results.map((activo: any) => (
                                        <TableRow key={activo.id}>
                                            <TableCell>{activo.nombre}</TableCell>
                                            <TableCell>{activo.categoria_nombre}</TableCell>
                                            <TableCell>${activo.valor_adquisicion}</TableCell>
                                            <TableCell>${activo.valor_en_libros}</TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        )}
                         {!activosLoading && (!activos || activos.results.length === 0) && (
                            <p className="text-center text-gray-500 py-8">No hay activos fijos registrados.</p>
                        )}
                    </CardContent>
                </Card>

                {/* Sección de Últimas Depreciaciones */}
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between">
                        <CardTitle>Depreciaciones Recientes</CardTitle>
                         <Button size="sm">
                            <PlusCircle className="mr-2 h-4 w-4" /> Registrar Depreciación
                        </Button>
                    </CardHeader>
                    <CardContent>
                        {depreciacionesLoading && <p>Cargando depreciaciones...</p>}
                        {!depreciacionesLoading && depreciaciones && (
                             <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Fecha</TableHead>
                                        <TableHead>Activo</TableHead>
                                        <TableHead>Valor</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {depreciaciones.results.slice(0, 10).map((dep: any) => (
                                        <TableRow key={dep.id}>
                                            <TableCell>{format(new Date(dep.fecha), 'dd/MM/yyyy')}</TableCell>
                                            <TableCell>{/* Aquí necesitaríamos el nombre del activo */}</TableCell>
                                            <TableCell>${dep.valor}</TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        )}
                        {!depreciacionesLoading && (!depreciaciones || depreciaciones.results.length === 0) && (
                           <p className="text-center text-gray-500 py-8">No hay depreciaciones recientes.</p>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default ActivosPage;
