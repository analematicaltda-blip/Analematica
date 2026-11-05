'use client';

import React, { useState, useEffect } from 'react';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FiPlus, FiTrash2, FiSave, FiArrowLeft } from 'react-icons/fi';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { toast } from 'react-toastify';

export default function NuevoAsientoPage() {
  const router = useRouter();
  const { getChartOfAccounts, createAsientoContable } = useMiNegocioApi();
  const [accounts, setAccounts] = useState<any[]>([]);
  const [description, setDescription] = useState('');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [lines, setLines] = useState([
    { cuenta_id: '', debito: 0, credito: 0, descripcion: '' },
    { cuenta_id: '', debito: 0, credito: 0, descripcion: '' },
  ]);

  useEffect(() => {
    const loadAccounts = async () => {
      const data = await getChartOfAccounts();
      if (data) setAccounts(data);
    };
    loadAccounts();
  }, [getChartOfAccounts]);

  const addLine = () => {
    setLines([...lines, { cuenta_id: '', debito: 0, credito: 0, descripcion: '' }]);
  };

  const removeLine = (index: number) => {
    setLines(lines.filter((_, i) => i !== index));
  };

  const updateLine = (index: number, field: string, value: any) => {
    const newLines = [...lines];
    newLines[index] = { ...newLines[index], [field]: value };
    setLines(newLines);
  };

  const totalDebito = lines.reduce((acc, line) => acc + Number(line.debito), 0);
  const totalCredito = lines.reduce((acc, line) => acc + Number(line.credito), 0);
  const isBalanced = totalDebito === totalCredito && totalDebito > 0;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isBalanced) {
      toast.error("El asiento debe estar balanceado y ser mayor a cero.");
      return;
    }

    const data = {
      fecha: date,
      descripcion: description,
      transacciones: lines.map(l => ({
        cuenta_id: l.cuenta_id,
        debito: l.debito,
        credito: l.credito,
        descripcion: l.descripcion || description
      }))
    };

    const res = await createAsientoContable(data);
    if (res) {
      toast.success("Asiento creado con éxito.");
      router.push('/dashboard/prestador/mi-negocio/gestion-contable/asientos');
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto py-8">
      <div className="flex items-center gap-4">
        <Link href="/dashboard/prestador/mi-negocio/gestion-contable/asientos">
          <Button variant="ghost" size="sm"><FiArrowLeft className="mr-2" /> Volver</Button>
        </Link>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Nuevo Asiento Contable</h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <Card className="border-none shadow-sm">
          <CardContent className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-widest text-slate-500">Fecha del Asiento</label>
              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="w-full p-3 bg-slate-50 rounded-xl border-none outline-none focus:ring-2 ring-brand/20"
                required
              />
            </div>
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-widest text-slate-500">Descripción General</label>
              <input
                type="text"
                placeholder="Ej: Venta de servicios turísticos"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full p-3 bg-slate-50 rounded-xl border-none outline-none focus:ring-2 ring-brand/20"
                required
              />
            </div>
          </CardContent>
        </Card>

        <Card className="border-none shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg font-bold uppercase tracking-tighter">Partida Doble</CardTitle>
            <Button type="button" onClick={addLine} variant="outline" size="sm"><FiPlus className="mr-2"/> Agregar Línea</Button>
          </CardHeader>
          <CardContent className="p-0">
            <table className="w-full text-left border-collapse">
              <thead className="bg-slate-50 text-[10px] font-black uppercase tracking-widest text-slate-400">
                <tr>
                  <th className="p-4">Cuenta</th>
                  <th className="p-4">Descripción (Opcional)</th>
                  <th className="p-4 w-32">Débito</th>
                  <th className="p-4 w-32">Crédito</th>
                  <th className="p-4 w-12"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {lines.map((line, index) => (
                  <tr key={index}>
                    <td className="p-4">
                      <select
                        value={line.cuenta_id}
                        onChange={(e) => updateLine(index, 'cuenta_id', e.target.value)}
                        className="w-full p-2 bg-transparent text-sm border rounded-lg"
                        required
                      >
                        <option value="">Seleccione una cuenta...</option>
                        {accounts.map(acc => (
                          <option key={acc.id} value={acc.id}>{acc.code} - {acc.name}</option>
                        ))}
                      </select>
                    </td>
                    <td className="p-4">
                      <input
                        type="text"
                        value={line.descripcion}
                        onChange={(e) => updateLine(index, 'descripcion', e.target.value)}
                        className="w-full p-2 bg-transparent text-sm border rounded-lg"
                      />
                    </td>
                    <td className="p-4">
                      <input
                        type="number"
                        value={line.debito}
                        onChange={(e) => updateLine(index, 'debito', e.target.value)}
                        className="w-full p-2 bg-transparent text-sm border rounded-lg text-right"
                      />
                    </td>
                    <td className="p-4">
                      <input
                        type="number"
                        value={line.credito}
                        onChange={(e) => updateLine(index, 'credito', e.target.value)}
                        className="w-full p-2 bg-transparent text-sm border rounded-lg text-right"
                      />
                    </td>
                    <td className="p-4">
                      {lines.length > 2 && (
                        <button type="button" onClick={() => removeLine(index)} className="text-slate-300 hover:text-red-500"><FiTrash2 /></button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot className="bg-slate-50 font-black text-sm">
                <tr>
                  <td colSpan={2} className="p-4 text-right uppercase tracking-widest text-[10px]">Totales</td>
                  <td className={`p-4 text-right ${totalDebito !== totalCredito ? 'text-red-500' : 'text-green-600'}`}>${totalDebito.toLocaleString()}</td>
                  <td className={`p-4 text-right ${totalDebito !== totalCredito ? 'text-red-500' : 'text-green-600'}`}>${totalCredito.toLocaleString()}</td>
                  <td></td>
                </tr>
              </tfoot>
            </table>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-4">
          <Button type="button" variant="ghost" onClick={() => router.back()}>Cancelar</Button>
          <Button type="submit" disabled={!isBalanced} className="bg-brand hover:bg-brand-light text-white px-12 py-6 rounded-2xl shadow-xl shadow-brand/20 font-black uppercase tracking-widest transition-all">
            <FiSave className="mr-2" /> Guardar Asiento
          </Button>
        </div>
      </form>
    </div>
  );
}
