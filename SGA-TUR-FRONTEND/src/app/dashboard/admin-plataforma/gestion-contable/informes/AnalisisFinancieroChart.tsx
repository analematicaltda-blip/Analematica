'use client';
import React, { useEffect, useState } from 'react';
import { useMiNegocioApi } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface IngresosGastosData {
  mes: string;
  ingresos: number;
  gastos: number;
}

export default function AnalisisFinancieroChart() {
  const { getReporteIngresosGastos, isLoading } = useMiNegocioApi();
  const [reportData, setReportData] = useState<IngresosGastosData[]>([]);

  useEffect(() => {
    const fetchReportData = async () => {
      const data = await getReporteIngresosGastos();
      if (data && data.length > 0) {
        setReportData(data);
      }
    };
    fetchReportData();
  }, [getReporteIngresosGastos]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Análisis Financiero: Ingresos vs. Gastos</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p>Cargando datos del informe...</p>
        ) : reportData.length > 0 ? (
          <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
              <BarChart data={reportData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="mes" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="ingresos" fill="#82ca9d" name="Ingresos" />
                <Bar dataKey="gastos" fill="#8884d8" name="Gastos" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p>No hay datos disponibles para mostrar en el gráfico.</p>
        )}
      </CardContent>
    </Card>
  );
}
