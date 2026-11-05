// frontend/src/app/dashboard/prestador/mi-negocio/gestion-financiera/[cuentaId]/page.tsx
'use client';
import React, { useEffect, useState, useCallback } from 'react';
import { useParams } from 'next/navigation';
import { useMiNegocioApi, BankAccount, CashTransaction } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { toast } from 'react-toastify';
import Modal from '@/components/ui/Modal';
import TransaccionForm from '../components/TransaccionForm';

type FormValues = {
  tipo: 'INGRESO' | 'EGRESO';
  monto: number;
  descripcion: string;
};

export default function CuentaDetallePage() {
  const params = useParams();
  const cuentaId = params.cuentaId as string;

  const { getBankAccounts, getCashTransactions, createCashTransaction, isLoading } = useMiNegocioApi();
  const [cuenta, setCuenta] = useState<BankAccount | null>(null);
  const [transacciones, setTransacciones] = useState<CashTransaction[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchAllData = useCallback(async () => {
    if (!cuentaId) return;

    // Fetch account details
    const accountsData = await getBankAccounts();
    if (accountsData && accountsData.results) {
      const cuentaEncontrada = accountsData.results.find((c: BankAccount) => c.id === parseInt(cuentaId));
      setCuenta(cuentaEncontrada || null);

      // Fetch transactions only after account is found
      if (cuentaEncontrada) {
        const transData = await getCashTransactions();
        if (transData && transData.results) {
          const transaccionesFiltradas = transData.results.filter((t: any) => t.cuenta === cuentaEncontrada.id);
          setTransacciones(transaccionesFiltradas);
        }
      }
    }
  }, [cuentaId, getBankAccounts, getCashTransactions]);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  const handleSubmit = async (values: FormValues) => {
    const apiData = {
      cuenta: parseInt(cuentaId),
      tipo: values.tipo,
      monto: values.monto.toString(),
      descripcion: values.descripcion,
      fecha: new Date().toISOString().split('T')[0], // Today's date
    };

    const success = await createCashTransaction(apiData);
    if (success) {
      toast.success("Transacción registrada con éxito.");
      setIsModalOpen(false);
      fetchAllData(); // Refresh all data
    }
  };

  if (isLoading && !cuenta) return <p>Cargando detalles de la cuenta...</p>;
  if (!cuenta) return <p>Cuenta no encontrada.</p>;

  return (
    <>
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>{cuenta.bank_name} - {cuenta.account_holder}</CardTitle>
            <CardDescription>
              Cuenta {cuenta.account_type === 'SAVINGS' ? 'de Ahorros' : 'Corriente'} No. {cuenta.account_number}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Saldo Actual: ${cuenta.balance}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Historial de Transacciones</CardTitle>
              <Button onClick={() => setIsModalOpen(true)}>
                Nueva Transacción
              </Button>
          </CardHeader>
          <CardContent>
             <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Fecha</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Descripción</TableHead>
                  <TableHead>Monto</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {transacciones.map((t) => (
                  <TableRow key={t.id}>
                    <TableCell>{new Date(t.date).toLocaleDateString()}</TableCell>
                    <TableCell>{t.transaction_type}</TableCell>
                    <TableCell>{t.description}</TableCell>
                    <TableCell className={t.transaction_type === 'DEPOSIT' ? 'text-green-600' : 'text-red-600'}>
                      ${t.amount}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>

      {isModalOpen && (
        <Modal title="Nueva Transacción" isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
          <TransaccionForm onSubmit={handleSubmit} isSubmitting={isLoading} />
        </Modal>
      )}
    </>
  );
}
