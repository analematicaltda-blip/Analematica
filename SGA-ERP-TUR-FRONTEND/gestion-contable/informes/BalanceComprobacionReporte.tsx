'use client';
import React, { useState, useEffect } from 'react';
import { useMiNegocioApi } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';

interface BalanceComprobacionData {
    detalle: { codigo: string; nombre: string; debito: number; credito: number }[];
    totales: { debitos: number; creditos: number };
}

export default function BalanceComprobacionReporte() {
    const { getBalanceComprobacion, isLoading } = useMiNegocioApi();
    const [reportData, setReportData] = useState<BalanceComprobacionData | null>(null);
    const [fechaFin, setFechaFin] = useState(new Date().toISOString().split('T')[0]);

    const handleGenerateReport = async () => {
        const data = await getBalanceComprobacion({ fecha_fin: fechaFin });
        setReportData(data);
    };

    useEffect(() => {
        handleGenerateReport();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);


    return (
        <Card>
            <CardHeader>
                <CardTitle>Balance de Comprobación</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="flex gap-4 mb-4">
                    <Input type="date" value={fechaFin} onChange={(e) => setFechaFin(e.target.value)} />
                    <Button onClick={handleGenerateReport} disabled={isLoading}>
                        {isLoading ? 'Generando...' : 'Generar Reporte'}
                    </Button>
                </div>
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Código</TableHead>
                            <TableHead>Nombre de Cuenta</TableHead>
                            <TableHead className="text-right">Débito</TableHead>
                            <TableHead className="text-right">Crédito</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {reportData?.detalle.map((row) => (
                            <TableRow key={row.codigo}>
                                <TableCell>{row.codigo}</TableCell>
                                <TableCell>{row.nombre}</TableCell>
                                <TableCell className="text-right">{row.debito.toFixed(2)}</TableCell>
                                <TableCell className="text-right">{row.credito.toFixed(2)}</TableCell>
                            </TableRow>
                        ))}
                        <TableRow className="font-bold">
                            <TableCell colSpan={2}>Totales</TableCell>
                            <TableCell className="text-right">{reportData?.totales.debitos.toFixed(2)}</TableCell>
                            <TableCell className="text-right">{reportData?.totales.creditos.toFixed(2)}</TableCell>
                        </TableRow>
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    );
}
