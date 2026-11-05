'use client';
import React, { useState } from 'react';
import { useMiNegocioApi } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';

interface TransaccionLibroMayor {
    journal_entry_date: string;
    journal_entry_description: string;
    debit: string;
    credit: string;
}

export default function LibroMayorReporte() {
    const { getLibroMayor, isLoading } = useMiNegocioApi();
    const [transactions, setTransactions] = useState<TransaccionLibroMayor[]>([]);
    const [cuenta, setCuenta] = useState('');
    const [fechaInicio, setFechaInicio] = useState('');
    const [fechaFin, setFechaFin] = useState('');
    const [error, setError] = useState('');

    const handleGenerateReport = async () => {
        if (!cuenta || !fechaInicio || !fechaFin) {
            setError('Todos los campos son requeridos.');
            return;
        }
        setError('');
        const data = await getLibroMayor({ codigo_cuenta: cuenta, fecha_inicio: fechaInicio, fecha_fin: fechaFin });
        if (data) {
            setTransactions(data);
        } else {
            setTransactions([]);
        }
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>Libro Mayor por Cuenta</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="flex gap-4 mb-4">
                    <Input placeholder="Código de Cuenta (ej: 110505)" value={cuenta} onChange={(e) => setCuenta(e.target.value)} />
                    <Input type="date" value={fechaInicio} onChange={(e) => setFechaInicio(e.target.value)} />
                    <Input type="date" value={fechaFin} onChange={(e) => setFechaFin(e.target.value)} />
                    <Button onClick={handleGenerateReport} disabled={isLoading}>
                        {isLoading ? 'Generando...' : 'Generar Reporte'}
                    </Button>
                </div>
                {error && <p className="text-red-500">{error}</p>}
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Fecha</TableHead>
                            <TableHead>Descripción</TableHead>
                            <TableHead className="text-right">Débito</TableHead>
                            <TableHead className="text-right">Crédito</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {transactions.map((tx, index) => (
                            <TableRow key={index}>
                                <TableCell>{new Date(tx.journal_entry_date).toLocaleDateString()}</TableCell>
                                <TableCell>{tx.journal_entry_description}</TableCell>
                                <TableCell className="text-right">{tx.debit}</TableCell>
                                <TableCell className="text-right">{tx.credit}</TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    );
}
