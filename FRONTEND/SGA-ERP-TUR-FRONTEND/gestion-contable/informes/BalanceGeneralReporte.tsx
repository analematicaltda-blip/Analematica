'use client';
import React, { useState, useEffect } from 'react';
import { useMiNegocioApi } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';

interface ReporteFinancieroData {
    detalle: { codigo: string; nombre: string; saldo: number }[];
    total: number;
}

export default function BalanceGeneralReporte() {
    const { getReporteFinanciero, isLoading } = useMiNegocioApi();
    const [reportData, setReportData] = useState<ReporteFinancieroData | null>(null);
    const [fechaFin, setFechaFin] = useState(new Date().toISOString().split('T')[0]);

    const handleGenerateReport = async () => {
        const data = await getReporteFinanciero({ reporte: 'balance_general', fecha_fin: fechaFin });
        setReportData(data);
    };

    useEffect(() => {
        handleGenerateReport();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (
        <Card>
            <CardHeader>
                <CardTitle>Balance General</CardTitle>
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
                            <TableHead>Cuenta</TableHead>
                            <TableHead className="text-right">Saldo</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {reportData?.detalle.map((row) => (
                            <TableRow key={row.codigo}>
                                <TableCell>{row.codigo} - {row.nombre}</TableCell>
                                <TableCell className="text-right">{row.saldo.toFixed(2)}</TableCell>
                            </TableRow>
                        ))}
                        <TableRow className="font-bold">
                            <TableCell>Total (Activo = Pasivo + Patrimonio)</TableCell>
                            <TableCell className="text-right">{reportData?.total.toFixed(2)}</TableCell>
                        </TableRow>
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    );
}
