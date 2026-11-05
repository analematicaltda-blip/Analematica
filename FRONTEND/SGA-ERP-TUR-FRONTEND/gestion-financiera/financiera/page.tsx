'use client';
import React, { useEffect, useState } from 'react';
import { useMiNegocioApi } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { TrendingUp, TrendingDown, DollarSign } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const AnalisisFinancieroPage = () => {
    const { getReporteIngresosGastos, isLoading } = useMiNegocioApi(); // Corregido
    const [reporte, setReporte] = useState<any>(null);

    useEffect(() => {
        async function loadReporte() {
            const data = await getReporteIngresosGastos(); // Suponiendo que existe
            if(data) setReporte(data);
        }
        loadReporte();
    }, [getReporteIngresosGastos]);

    const chartData = [
        { name: 'Finanzas', ingresos: reporte?.total_ingresos || 0, gastos: reporte?.total_gastos || 0 },
    ];

    const formatCurrency = (value: number) => {
        return `$${(value || 0).toLocaleString('es-CO', { maximumFractionDigits: 0 })}`;
    };

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4">Análisis Financiero</h1>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                {/* Card Ingresos */}
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Ingresos</CardTitle>
                        <TrendingUp className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        {reporteLoading ? (
                            <div className="h-8 bg-gray-200 rounded animate-pulse"></div>
                        ) : (
                            <div className="text-2xl font-bold">{formatCurrency(reporteIngresosGastos?.total_ingresos)}</div>
                        )}
                        <p className="text-xs text-muted-foreground">En el período seleccionado</p>
                    </CardContent>
                </Card>

                {/* Card Gastos */}
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Gastos</CardTitle>
                        <TrendingDown className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        {reporteLoading ? (
                            <div className="h-8 bg-gray-200 rounded animate-pulse"></div>
                        ) : (
                            <div className="text-2xl font-bold">{formatCurrency(reporteIngresosGastos?.total_gastos)}</div>
                        )}
                        <p className="text-xs text-muted-foreground">En el período seleccionado</p>
                    </CardContent>
                </Card>

                {/* Card Neto */}
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Resultado Neto</CardTitle>
                        <DollarSign className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        {reporteLoading ? (
                             <div className="h-8 bg-gray-200 rounded animate-pulse"></div>
                        ) : (
                            <div className={`text-2xl font-bold ${reporteIngresosGastos?.neto >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {formatCurrency(reporteIngresosGastos?.neto)}
                            </div>
                        )}
                        <p className="text-xs text-muted-foreground">Ingresos - Gastos</p>
                    </CardContent>
                </Card>
            </div>

            <Card className="mt-6">
                <CardHeader>
                    <CardTitle>Resumen Gráfico</CardTitle>
                </CardHeader>
                <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={chartData}>
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip formatter={(value) => formatCurrency(value as number)} />
                            <Legend />
                            <Bar dataKey="ingresos" fill="#82ca9d" name="Ingresos" />
                            <Bar dataKey="gastos" fill="#8884d8" name="Gastos" />
                        </BarChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>

        </div>
    );
};

export default AnalisisFinancieroPage;
