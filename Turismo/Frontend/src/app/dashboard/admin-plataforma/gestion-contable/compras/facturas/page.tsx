'use client';
import { useEffect, useState } from 'react';
import { useMiNegocioApi, FacturaCompra } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/skeleton';
import { toast } from 'react-toastify';
import Link from 'next/link';
import { PlusCircle } from 'lucide-react';

const FacturasCompraPage = () => {
  const { getFacturasCompra, isLoading } = useMiNegocioApi();
  const [facturas, setFacturas] = useState<FacturaCompra[]>([]);

  useEffect(() => {
    const fetchFacturas = async () => {
      const data = await getFacturasCompra();
      if (data) setFacturas(data.results);
      else toast.error('No se pudieron cargar las facturas de compra.');
    };
    fetchFacturas();
  }, [getFacturasCompra]);

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Facturas de Compra</h1>
        <Link href="/dashboard/prestador/mi-negocio/gestion-contable/compras/facturas/nuevo" passHref>
          <Button><PlusCircle className="h-4 w-4 mr-2" />Registrar Factura</Button>
        </Link>
      </div>

      <Card>
        <CardHeader><CardTitle>Historial de Facturas</CardTitle></CardHeader>
        <CardContent>
          {isLoading && facturas.length === 0 ? (
            <div className="space-y-2"><Skeleton className="h-10 w-full" /><Skeleton className="h-10 w-full" /></div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Número</TableHead><TableHead>Proveedor</TableHead><TableHead>Fecha Emisión</TableHead>
                  <TableHead>Estado</TableHead><TableHead className="text-right">Total</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {facturas.length > 0 ? facturas.map((factura) => (
                    <TableRow key={factura.id}>
                      <TableCell>#{factura.number}</TableCell>
                      <TableCell>{factura.proveedor_nombre || 'N/A'}</TableCell>
                      <TableCell>{factura.issue_date}</TableCell>
                      <TableCell>{factura.estado}</TableCell>
                      <TableCell className="text-right">${Number(factura.total).toFixed(2)}</TableCell>
                    </TableRow>
                  )) : (
                  <TableRow><TableCell colSpan={5} className="text-center">No hay facturas registradas.</TableCell></TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default FacturasCompraPage;
