'use client';
import { useEffect, useState } from 'react';
import { useMiNegocioApi, FacturaVenta } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { useComercialApi } from '../hooks/useComercialApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Skeleton } from '@/components/ui/skeleton';
import { toast } from 'react-toastify';
import Link from 'next/link';
import { PlusCircle, Send, ShieldCheck } from 'lucide-react';

const FacturasVentaPage = () => {
  const { getFacturasVenta, isLoading } = useMiNegocioApi();
  const { sendDian } = useComercialApi();
  const [facturas, setFacturas] = useState<FacturaVenta[]>([]);

  const handleSendDian = async (id: string) => {
    try {
      await sendDian(id);
      toast.success('Enviado a la DIAN correctamente.');
      // Refresh
      const data = await getFacturasVenta();
      if (data) setFacturas(data);
    } catch (e) {
      toast.error('Error al enviar a la DIAN.');
    }
  };

  useEffect(() => {
    const fetchFacturas = async () => {
      const data = await getFacturasVenta();
      if (data) {
        setFacturas(data);
      } else {
        toast.error('No se pudieron cargar las facturas.');
      }
    };
    fetchFacturas();
  }, [getFacturasVenta]);

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Facturas de Venta</h1>
        <Link href="/dashboard/prestador/mi-negocio/gestion-comercial/facturas-venta/nuevo" passHref>
          <Button><PlusCircle className="h-4 w-4 mr-2" />Crear Factura</Button>
        </Link>
      </div>

      <Card>
        <CardHeader><CardTitle>Historial de Facturas</CardTitle></CardHeader>
        <CardContent>
          {isLoading && facturas.length === 0 ? (
            <div className="space-y-2">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Número</TableHead>
                  <TableHead>Cliente</TableHead>
                  <TableHead>Fecha Emisión</TableHead>
                  <TableHead>Estado DIAN</TableHead>
                  <TableHead className="text-right">Total</TableHead>
                  <TableHead className="text-center">Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {facturas.length > 0 ? (
                  facturas.map((factura: any) => (
                    <TableRow key={factura.id}>
                      <TableCell className="font-mono">{factura.number || `#${factura.id}`}</TableCell>
                      <TableCell>{factura.cliente_nombre || 'N/A'}</TableCell>
                      <TableCell>{factura.issue_date}</TableCell>
                      <TableCell>
                        {factura.estado_dian === 'ACEPTADA' ? (
                          <Badge variant="success"><ShieldCheck className="w-3 h-3 mr-1" />Aceptada</Badge>
                        ) : factura.estado_dian === 'RECHAZADA' ? (
                          <Badge variant="destructive">Rechazada</Badge>
                        ) : (
                          <Badge variant="outline">Pendiente</Badge>
                        )}
                      </TableCell>
                      <TableCell className="text-right">${Number(factura.total).toFixed(2)}</TableCell>
                      <TableCell className="text-center">
                        {factura.estado_dian !== 'ACEPTADA' && (
                          <Button variant="ghost" size="sm" onClick={() => handleSendDian(factura.id)}>
                            <Send className="w-4 h-4" />
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center">No hay facturas registradas.</TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default FacturasVentaPage;
