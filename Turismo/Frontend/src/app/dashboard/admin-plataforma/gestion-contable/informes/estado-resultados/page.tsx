// /app/dashboard/prestador/mi-negocio/gestion-contable/informes/estado-resultados/page.tsx
'use client';
import { useState } from 'react';
import { useMiNegocioApi, EstadoResultadosData } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import DateRangePicker from '../../components/DateRangePicker';
export default function EstadoResultadosPage() {
  const { getEstadoResultados, isLoading } = useMiNegocioApi();
  const [data, setData] = useState<EstadoResultadosData | null>(null);
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const result = await getEstadoResultados(formData.get('start_date') as string, formData.get('end_date') as string);
    if (result) setData(result);
  };
  return (
    <div className="p-4"><h1 className="text-2xl font-bold mb-4">Estado de Resultados</h1>
      <DateRangePicker onSubmit={handleSubmit} isLoading={isLoading} />
      {isLoading && <p>Cargando...</p>}
      {data && (
        <div className="mt-4 bg-white p-6 shadow rounded-lg max-w-md mx-auto">
          <div className="flex justify-between py-2 border-b"><span>Ingresos</span><span className="font-mono">{parseFloat(data.ingresos).toFixed(2)}</span></div>
          <div className="flex justify-between py-2 border-b"><span>Gastos</span><span className="font-mono text-red-600">({parseFloat(data.gastos).toFixed(2)})</span></div>
          <div className="flex justify-between py-2 font-bold text-lg"><span>Utilidad Neta</span><span className="font-mono">{parseFloat(data.utilidad_neta).toFixed(2)}</span></div>
        </div>
      )}
    </div>
  );
}
