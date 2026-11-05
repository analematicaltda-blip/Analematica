// frontend/src/app/dashboard/prestador/mi-negocio/gestion-contable/inventario/components/ProductosTab.tsx
'use client';
import React, { useState, useCallback, useEffect } from 'react';
import { useMiNegocioApi, Producto } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import ProductoForm from './ProductoForm';
import { toast } from 'react-toastify';
import { Input } from '@/components/ui/Input';

export default function ProductosTab() {
  const { getProductos, createProducto, updateProducto, deleteProducto, isLoading } = useMiNegocioApi();
  const [productos, setProductos] = useState<Producto[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedProducto, setSelectedProducto] = useState<Producto | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredProductos = productos.filter(p =>
    p.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.sku.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const fetchProductos = useCallback(async () => {
    const data = await getProductos();
    if (data && data.results) setProductos(data.results);
  }, [getProductos]);

  useEffect(() => {
    fetchProductos();
  }, [fetchProductos]);

  const handleOpenModal = (producto: Producto | null = null) => {
    setSelectedProducto(producto);
    setIsModalOpen(true);
  };

  const handleSubmit = async (values: any) => {
    let success;
    if (selectedProducto) {
      success = await updateProducto(selectedProducto.id, values);
    } else {
      success = await createProducto(values);
    }
    if (success) {
      fetchProductos();
      setIsModalOpen(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('¿Seguro que quieres eliminar este producto?')) {
      const success = await deleteProducto(id);
      if (success) {
        toast.success('Producto eliminado');
        fetchProductos();
      }
    }
  };

  return (
    <>
      <div className="flex justify-between items-center mb-4">
        <Input
          placeholder="Buscar por SKU o nombre..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="max-w-sm"
        />
        <Button onClick={() => handleOpenModal()}>Nuevo Producto</Button>
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>SKU</TableHead>
            <TableHead>Nombre</TableHead>
            <TableHead>Costo</TableHead>
            <TableHead>Precio Venta</TableHead>
            <TableHead>Stock Actual</TableHead>
            <TableHead>Acciones</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filteredProductos.map((p) => (
            <TableRow key={p.id}>
              <TableCell>{p.sku}</TableCell>
              <TableCell>{p.nombre}</TableCell>
              <TableCell>${p.costo}</TableCell>
              <TableCell>${p.precio_venta}</TableCell>
              <TableCell>{p.stock_actual}</TableCell>
              <TableCell>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" onClick={() => handleOpenModal(p)}>Editar</Button>
                  <Button variant="destructive" size="sm" onClick={() => handleDelete(p.id)}>Eliminar</Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {isModalOpen && (
        <Modal title={selectedProducto ? 'Editar Producto' : 'Nuevo Producto'} isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
          <ProductoForm
            onSubmit={handleSubmit}
            initialData={selectedProducto || undefined}
            isSubmitting={isLoading}
          />
        </Modal>
      )}
    </>
  );
}
