// /app/dashboard/prestador/mi-negocio/gestion-contable/informes/sumas-y-saldos/page.tsx
'use client';
import { useState } from 'react';
import { useMiNegocioApi, SumasSaldosEntry } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
export default function SumasSaldosPage() {
  const { getSumasYSaldos, isLoading } = useMiNegocioApi();
  const [data, setData] = useState<SumasSaldosEntry[]>([]);
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const result = await getSumasYSaldos(formData.get('end_date') as string);
    if (result) setData(result);
  };
  return (
    <div className="p-4"><h1 className="text-2xl font-bold mb-4">Balance de Sumas y Saldos</h1>
      <form onSubmit={handleSubmit}><input type="date" name="end_date"/><button type="submit">Generar</button></form>
      {isLoading && <p>Cargando...</p>}
      <table className="min-w-full bg-white shadow mt-4">
        <thead><tr className="bg-gray-100"><th>Cuenta</th><th className="text-right">Débito</th><th className="text-right">Crédito</th><th className="text-right">Saldo</th></tr></thead>
        <tbody>
          {data.map(entry => (
            <tr key={entry.account.id}>
              <td>{entry.account.account_number} - {entry.account.name}</td>
              <td className="text-right font-mono">{parseFloat(entry.total_debit).toFixed(2)}</td>
              <td className="text-right font-mono">{parseFloat(entry.total_credit).toFixed(2)}</td>
              <td className="text-right font-mono">{parseFloat(entry.balance).toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
