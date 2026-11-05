'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useMiNegocioApi, Cliente, ItemFactura, Producto } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Label } from '@/components/ui/Label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { toast } from 'react-toastify';
import { PlusCircle, Trash2 } from 'lucide-react';

export default function NuevaVentaPage() {
  const { createFacturaVenta, getClientes, getProductos, isLoading } = useMiNegocioApi();
  const router = useRouter();
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [productos, setProductos] = useState<Producto[]>([]);
  const [selectedCliente, setSelectedCliente] = useState<string>('');
  const [fechaEmision, setFechaEmision] = useState(new Date().toISOString().split('T')[0]);
  const [fechaVencimiento, setFechaVencimiento] = useState(new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]);
  const [items, setItems] = useState<Partial<ItemFactura>[]>([
    { producto: undefined, cantidad: 1, precio_unitario: '0' }
  ]);

  useEffect(() => {
    const fetchData = async () => {
      const clientesData = await getClientes();
      if (clientesData) setClientes(clientesData.results);

      const productosData = await getProductos();
      if (productosData) setProductos(productosData.results);
    };
    fetchData();
  }, [getClientes, getProductos]);

  const handleItemChange = (index: number, field: keyof ItemFactura, value: any) => {
    const newItems = [...items];
    const item = newItems[index];
    (item[field] as any) = value;

    // Si se cambia el producto, actualizar el precio
    if (field === 'producto') {
      const productoSeleccionado = productos.find(p => p.id === Number(value));
      if (productoSeleccionado) {
        item.precio_unitario = productoSeleccionado.precio_venta;
      }
    }

    setItems(newItems);
  };

  const addItem = () => {
    setItems([...items, { producto: undefined, cantidad: 1, precio_unitario: '0' }]);
  };

  const removeItem = (index: number) => {
    const newItems = items.filter((_, i) => i !== index);
    setItems(newItems);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCliente || items.some(item => !item.producto || item.cantidad <= 0)) {
      toast.error('Por favor, complete todos los campos requeridos.');
      return;
    }

    const facturaData = {
      cliente: Number(selectedCliente),
      issue_date: fechaEmision,
      fecha_vencimiento: fechaVencimiento,
      items: items.map(item => ({
        producto: item.producto!,
        cantidad: Number(item.cantidad),
        precio_unitario: item.precio_unitario!,
      })),
    };

    const result = await createFacturaVenta(facturaData);
    if (result) {
      toast.success('Factura creada con éxito');
      router.push('/dashboard/prestador/mi-negocio/gestion-comercial/ventas');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Card>
        <CardHeader>
          <CardTitle>Crear Nueva Factura de Venta</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="cliente">Cliente</Label>
              <Select onValueChange={setSelectedCliente} value={selectedCliente}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione un cliente" />
                </SelectTrigger>
                <SelectContent>
                  {clientes.map(c => (
                    <SelectItem key={c.id} value={String(c.id)}>{c.nombre}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="fechaEmision">Fecha de Emisión</Label>
              <Input id="fechaEmision" type="date" value={fechaEmision} onChange={e => setFechaEmision(e.target.value)} />
            </div>
            <div>
              <Label htmlFor="fechaVencimiento">Fecha de Vencimiento</Label>
              <Input id="fechaVencimiento" type="date" value={fechaVencimiento} onChange={e => setFechaVencimiento(e.target.value)} />
            </div>
          </div>

          <div className="pt-4">
            <h3 className="text-lg font-semibold mb-2">Items de la Factura</h3>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Producto/Servicio</TableHead>
                  <TableHead className="w-[120px]">Cantidad</TableHead>
                  <TableHead className="w-[150px]">Precio Unitario</TableHead>
                  <TableHead className="w-[150px]">Total</TableHead>
                  <TableHead className="w-[50px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((item, index) => (
                  <TableRow key={index}>
                    <TableCell>
                       <Select onValueChange={value => handleItemChange(index, 'producto', value)} value={String(item.producto || '')}>
                        <SelectTrigger>
                          <SelectValue placeholder="Seleccione un producto" />
                        </SelectTrigger>
                        <SelectContent>
                          {productos.map(p => (
                            <SelectItem key={p.id} value={String(p.id)}>{p.nombre}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </TableCell>
                    <TableCell>
                      <Input type="number" value={item.cantidad} onChange={e => handleItemChange(index, 'cantidad', e.target.value)} min="1" />
                    </TableCell>
                    <TableCell>
                      <Input type="number" value={item.precio_unitario} onChange={e => handleItemChange(index, 'precio_unitario', e.target.value)} step="0.01" />
                    </TableCell>
                    <TableCell>
                      ${(Number(item.cantidad || 0) * Number(item.precio_unitario || 0)).toFixed(2)}
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="icon" onClick={() => removeItem(index)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <Button type="button" variant="outline" size="sm" onClick={addItem} className="mt-4">
              <PlusCircle className="mr-2 h-4 w-4" />
              Añadir Item
            </Button>
          </div>

        </CardContent>
        <CardFooter className="flex justify-end">
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Guardando...' : 'Guardar Factura'}
          </Button>
        </CardFooter>
      </Card>
    </form>
  );
}
