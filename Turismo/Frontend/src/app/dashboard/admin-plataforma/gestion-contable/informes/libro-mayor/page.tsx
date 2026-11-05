// /app/dashboard/prestador/mi-negocio/gestion-contable/informes/libro-mayor/page.tsx
'use client';
import { useState } from 'react';
import { useMiNegocioApi, LibroMayorEntry } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import DateRangePicker from '../../components/DateRangePicker';
export default function LibroMayorPage() {
  const { getLibroMayor, isLoading } = useMiNegocioApi();
  const [data, setData] = useState<LibroMayorEntry[]>([]);
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const result = await getLibroMayor(formData.get('start_date') as string, formData.get('end_date') as string);
    if (result) setData(result);
  };
  return (
    <div className="p-4"><h1 className="text-2xl font-bold mb-4">Libro Mayor</h1>
      <DateRangePicker onSubmit={handleSubmit} isLoading={isLoading} />
      {isLoading && <p>Cargando...</p>}
      <div className="mt-4 space-y-6">
        {data.map(entry => (
          <div key={entry.account.id} className="bg-white p-4 shadow rounded-lg">
            <h2 className="text-xl font-semibold">{entry.account.account_number} - {entry.account.name}</h2>
            <table className="w-full text-sm mt-2">
              <thead><tr className="bg-gray-50"><th className="text-left">Fecha</th><th className="text-right">Débito</th><th className="text-right">Crédito</th><th className="text-right">Saldo</th></tr></thead>
              <tbody>
                <tr><td colSpan={3}>Saldo Inicial</td><td className="text-right font-mono">{parseFloat(entry.initial_balance).toFixed(2)}</td></tr>
                {entry.transactions.reduce((acc, t) => {
                  const saldo = acc.saldo + parseFloat(t.debit) - parseFloat(t.credit);
                  acc.rows.push(<tr key={t.id}><td>{/* entry date missing */}</td><td className="text-right">{t.debit}</td><td className="text-right">{t.credit}</td><td className="text-right">{saldo.toFixed(2)}</td></tr>);
                  acc.saldo = saldo;
                  return acc;
                }, {rows: [], saldo: parseFloat(entry.initial_balance)}).rows}
              </tbody>
            </table>
          </div>
        ))}
      </div>
    </div>
  );
}
