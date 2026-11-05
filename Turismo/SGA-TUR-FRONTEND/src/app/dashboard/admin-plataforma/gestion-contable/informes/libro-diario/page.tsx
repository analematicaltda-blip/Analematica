// /app/dashboard/prestador/mi-negocio/gestion-contable/informes/libro-diario/page.tsx
'use client';
import { useState } from 'react';
import { useMiNegocioApi, JournalEntry } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import DateRangePicker from '../../components/DateRangePicker';

export default function LibroDiarioPage() {
  const { getLibroDiario, isLoading } = useMiNegocioApi();
  const [data, setData] = useState<JournalEntry[]>([]);
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const result = await getLibroDiario(formData.get('start_date') as string, formData.get('end_date') as string);
    if (result) setData(result);
  };
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Libro Diario</h1>
      <DateRangePicker onSubmit={handleSubmit} isLoading={isLoading} />
      {isLoading && <p className="mt-4">Cargando...</p>}
      <div className="mt-4 space-y-4">
        {data.map(entry => (
          <div key={entry.id} className="bg-white p-4 shadow rounded-lg">
            <div className="flex justify-between border-b pb-2 mb-2">
              <h3 className="font-bold text-lg">Asiento #{entry.id}</h3>
              <span className="text-gray-600">{entry.date}</span>
            </div>
            <p className="text-gray-700 italic mb-2">{entry.description}</p>
            <table className="w-full text-sm">
              <thead><tr className="bg-gray-50"><th className="text-left p-2">Cuenta</th><th className="text-right p-2">Débito</th><th className="text-right p-2">Crédito</th></tr></thead>
              <tbody>{entry.transactions.map(t => (
                <tr key={t.id} className="border-t">
                  <td className="p-2">{t.account_number}</td>
                  <td className="text-right p-2 font-mono">{parseFloat(t.debit).toFixed(2)}</td>
                  <td className="text-right p-2 font-mono">{parseFloat(t.credit).toFixed(2)}</td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        ))}
      </div>
    </div>
  );
}
