'use client';
import React from 'react';
import { useFinancieraApi } from '@/app/dashboard/prestador/mi-negocio/hooks/useFinancieraApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { PlusCircle, Landmark } from 'lucide-react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { format } from 'date-fns';

const TesoreriaPage = () => {
    const {
        cuentas,
        cuentasLoading,
        transacciones,
        transaccionesLoading,
    } = useFinancieraApi();

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4 flex items-center">
                <Landmark className="mr-2" /> Tesorería
            </h1>

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                {/* Sección de Cuentas Bancarias */}
                <Card className="xl:col-span-1">
                    <CardHeader className="flex flex-row items-center justify-between">
                        <CardTitle>Cuentas Bancarias</CardTitle>
                        <Button size="sm">
                            <PlusCircle className="mr-2 h-4 w-4" /> Nueva Cuenta
                        </Button>
                    </CardHeader>
                    <CardContent>
                        {cuentasLoading && <p>Cargando cuentas...</p>}
                        {!cuentasLoading && cuentas && (
                            <div className="space-y-4">
                                {cuentas.results.map((cuenta: any) => (
                                    <div key={cuenta.id} className="p-3 bg-gray-50 rounded-lg">
                                        <p className="font-semibold">{cuenta.banco}</p>
                                        <p className="text-sm text-gray-600">{cuenta.numero_cuenta}</p>
                                        <p className="text-lg font-bold text-right">${parseFloat(cuenta.saldo_actual).toLocaleString('es-CO')}</p>
                                    </div>
                                ))}
                            </div>
                        )}
                         {!cuentasLoading && (!cuentas || cuentas.results.length === 0) && (
                            <p className="text-center text-gray-500 py-8">No hay cuentas bancarias.</p>
                        )}
                    </CardContent>
                </Card>

                {/* Sección de Transacciones */}
                <Card className="xl:col-span-2">
                    <CardHeader className="flex flex-row items-center justify-between">
                        <CardTitle>Últimas Transacciones</CardTitle>
                         <Button size="sm">
                            <PlusCircle className="mr-2 h-4 w-4" /> Nuevo Movimiento
                        </Button>
                    </CardHeader>
                    <CardContent>
                        {transaccionesLoading && <p>Cargando transacciones...</p>}
                        {!transaccionesLoading && transacciones && (
                             <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Fecha</TableHead>
                                        <TableHead>Descripción</TableHead>
                                        <TableHead>Tipo</TableHead>
                                        <TableHead className="text-right">Monto</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {transacciones.results.slice(0, 15).map((tx: any) => (
                                        <TableRow key={tx.id}>
                                            <TableCell>{format(new Date(tx.fecha), 'dd/MM/yyyy')}</TableCell>
                                            <TableCell>{tx.descripcion}</TableCell>
                                            <TableCell>{tx.tipo}</TableCell>
                                            <TableCell className={`text-right font-medium ${tx.tipo === 'INGRESO' ? 'text-green-600' : 'text-red-600'}`}>
                                                {tx.tipo === 'INGRESO' ? '+' : '-'}${parseFloat(tx.monto).toLocaleString('es-CO')}
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        )}
                        {!transaccionesLoading && (!transacciones || transacciones.results.length === 0) && (
                           <p className="text-center text-gray-500 py-8">No hay transacciones recientes.</p>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default TesoreriaPage;
