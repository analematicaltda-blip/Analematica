// frontend/src/app/dashboard/prestador/mi-negocio/gestion-contable/compras/components/FacturasCompraTab.tsx
'use client';
import React, { useState, useCallback, useEffect } from 'react';
import { useMiNegocioApi, FacturaCompra, BankAccount } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import Modal from '@/components/ui/Modal';
import FacturaCompraForm from './FacturaCompraForm';
import { toast } from 'react-toastify';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select';
import { Input } from '@/components/ui/Input';

export default function FacturasCompraTab() {
  const { getFacturasCompra, createFacturaCompra, updateFacturaCompra, pagarFacturaCompra, getBankAccounts, isLoading } = useMiNegocioApi();
  const [facturas, setFacturas] = useState<FacturaCompra[]>([]);
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isPayModalOpen, setIsPayModalOpen] = useState(false);
  const [selectedFactura, setSelectedFactura] = useState<FacturaCompra | null>(null);
  const [cuentasBancarias, setCuentasBancarias] = useState<BankAccount[]>([]);
  const [cuentaPagoSeleccionada, setCuentaPagoSeleccionada] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredFacturas = facturas.filter(f =>
    f.proveedor_nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
    f.number.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const fetchFacturas = useCallback(async () => {
    const data = await getFacturasCompra();
    if (data && data.results) setFacturas(data.results);
  }, [getFacturasCompra]);

  useEffect(() => {
    fetchFacturas();
  }, [fetchFacturas]);

  const handleOpenFormModal = (factura: FacturaCompra | null = null) => {
    setSelectedFactura(factura);
    setIsFormModalOpen(true);
  };

  const handleOpenPayModal = async (factura: FacturaCompra) => {
    const data = await getBankAccounts();
    if (data && data.results) setCuentasBancarias(data.results);
    setSelectedFactura(factura);
    setIsPayModalOpen(true);
  };

  const handleSubmit = async (values: any) => {
    const apiData = { ...values, proveedor: parseInt(values.proveedor) };
    let success;
    if (selectedFactura) {
      success = await updateFacturaCompra(selectedFactura.id, apiData);
    } else {
      success = await createFacturaCompra(apiData);
    }
    if (success) {
      fetchFacturas();
      setIsFormModalOpen(false);
    }
  };

  const handlePaySubmit = async () => {
    if (!selectedFactura || !cuentaPagoSeleccionada) {
      toast.error("Seleccione una cuenta bancaria.");
      return;
    }
    const success = await pagarFacturaCompra(selectedFactura.id, parseInt(cuentaPagoSeleccionada));
    if (success) {
      fetchFacturas();
      setIsPayModalOpen(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PAGADA': return <Badge className="bg-green-500">Pagada</Badge>;
      case 'POR_PAGAR': return <Badge className="bg-yellow-500">Por Pagar</Badge>;
      case 'VENCIDA': return <Badge className="bg-red-500">Vencida</Badge>;
      case 'BORRADOR': return <Badge variant="secondary">Borrador</Badge>;
      default: return <Badge>{status}</Badge>;
    }
  };

  return (
    <>
      <div className="flex justify-between items-center mb-4">
        <Input
          placeholder="Buscar por proveedor o número..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="max-w-sm"
        />
        <Button onClick={() => handleOpenFormModal()}>Nueva Factura</Button>
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Proveedor</TableHead>
            <TableHead>Número</TableHead>
            <TableHead>Fecha</TableHead>
            <TableHead>Total</TableHead>
            <TableHead>Estado</TableHead>
            <TableHead>Acciones</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filteredFacturas.map((f) => (
            <TableRow key={f.id}>
              <TableCell>{f.proveedor_nombre}</TableCell>
              <TableCell>{f.number}</TableCell>
              <TableCell>{new Date(f.issue_date).toLocaleDateString()}</TableCell>
              <TableCell>${f.total}</TableCell>
              <TableCell>{getStatusBadge(f.estado)}</TableCell>
              <TableCell>
                 <div className="flex space-x-2">
                  <Button variant="outline" size="sm" onClick={() => handleOpenFormModal(f)}>Editar</Button>
                  <Button size="sm" onClick={() => handleOpenPayModal(f)} disabled={f.estado !== 'POR_PAGAR'}>Pagar</Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {isFormModalOpen && (
        <Modal title={selectedFactura ? 'Editar Factura' : 'Nueva Factura'} isOpen={isFormModalOpen} onClose={() => setIsFormModalOpen(false)}>
          <FacturaCompraForm onSubmit={handleSubmit} initialData={selectedFactura || undefined} isSubmitting={isLoading} />
        </Modal>
      )}

      {isPayModalOpen && selectedFactura && (
        <Modal title={`Pagar Factura #${selectedFactura.number}`} isOpen={isPayModalOpen} onClose={() => setIsPayModalOpen(false)}>
          <div className="space-y-4">
            <p>Seleccione la cuenta bancaria para realizar el pago de <strong>${selectedFactura.total}</strong>.</p>
            <Select onValueChange={setCuentaPagoSeleccionada}>
              <SelectTrigger><SelectValue placeholder="Seleccione una cuenta..." /></SelectTrigger>
              <SelectContent>
                {cuentasBancarias.map(c => <SelectItem key={c.id} value={c.id.toString()}>{c.bank_name} - {c.account_number}</SelectItem>)}
              </SelectContent>
            </Select>
            <Button onClick={handlePaySubmit} disabled={isLoading || !cuentaPagoSeleccionada}>
              {isLoading ? 'Procesando...' : 'Confirmar Pago'}
            </Button>
          </div>
        </Modal>
      )}
    </>
  );
}
