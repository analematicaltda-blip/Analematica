// /app/dashboard/prestador/mi-negocio/gestion-contable/informes/balance-general/page.tsx
'use client';
import { useState } from 'react';
import { useMiNegocioApi, BalanceGeneralData } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
export default function BalanceGeneralPage() {
  const { getBalanceGeneral, isLoading } = useMiNegocioApi();
  const [data, setData] = useState<BalanceGeneralData | null>(null);
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const result = await getBalanceGeneral(formData.get('end_date') as string);
    if (result) setData(result);
  };
  return (
    <div className="p-4"><h1 className="text-2xl font-bold mb-4">Balance General</h1>
      <form onSubmit={handleSubmit}><input type="date" name="end_date"/><button type="submit">Generar</button></form>
      {isLoading && <p>Cargando...</p>}
      {data && (
        <div className="mt-4 grid grid-cols-2 gap-4">
          <div className="bg-white p-4 shadow rounded-lg">
            <h2 className="font-bold text-lg">Activos</h2><p className="font-mono">{parseFloat(data.asset).toFixed(2)}</p>
          </div>
          <div>
            <div className="bg-white p-4 shadow rounded-lg mb-4">
              <h2 className="font-bold text-lg">Pasivos</h2><p className="font-mono">{parseFloat(data.liability).toFixed(2)}</p>
            </div>
            <div className="bg-white p-4 shadow rounded-lg">
              <h2 className="font-bold text-lg">Patrimonio</h2><p className="font-mono">{parseFloat(data.equity).toFixed(2)}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
