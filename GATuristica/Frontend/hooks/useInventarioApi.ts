import useSWR from 'swr';
import { useApi } from '@/services/api';
import { useCallback } from 'react';

// --- Tipos de Datos ---
interface CategoriaProducto { id: number; nombre: string; descripcion?: string; }
interface Almacen { id: number; nombre: string; ubicacion?: string; }
interface Producto {
    id: number;
    nombre: string;
    sku: string;
    categoria?: number;
    categoria_nombre?: string;
    descripcion?: string;
    costo: string;
    precio_venta: string;
    stock_actual: string;
    stock_minimo: string;
}
interface MovimientoInventario {
    id: number;
    producto: number;
    producto_nombre: string;
    almacen: number;
    almacen_nombre: string;
    tipo_movimiento: string;
    cantidad: string;
    fecha: string;
    descripcion?: string;
}

export const useInventarioApi = () => {
    const { api } = useApi();
    const fetcher = (url: string) => api.get(url).then(res => res.data);

    // --- Categorías de Productos ---
    const { data: categorias, mutate: mutateCategorias } = useSWR('/mi-negocio/inventario/categorias/', fetcher);
    const createCategoria = useCallback(async (data: Omit<CategoriaProducto, 'id'>) => {
        await api.post('/mi-negocio/inventario/categorias/', data);
        mutateCategorias();
    }, [api, mutateCategorias]);

    // --- Almacenes ---
    const { data: almacenes, mutate: mutateAlmacenes } = useSWR('/mi-negocio/inventario/almacenes/', fetcher);
    const createAlmacen = useCallback(async (data: Omit<Almacen, 'id'>) => {
        await api.post('/mi-negocio/inventario/almacenes/', data);
        mutateAlmacenes();
    }, [api, mutateAlmacenes]);

    // --- Productos ---
    const { data: productos, error: productosError, mutate: mutateProductos } = useSWR('/mi-negocio/inventario/productos/', fetcher);
    const createProducto = useCallback(async (data: Omit<Producto, 'id' | 'categoria_nombre' | 'stock_actual'>) => {
        await api.post('/mi-negocio/inventario/productos/', data);
        mutateProductos();
    }, [api, mutateProductos]);
    const updateProducto = useCallback(async (id: number, data: Partial<Omit<Producto, 'id' | 'categoria_nombre' | 'stock_actual'>>) => {
        await api.patch(`/mi-negocio/inventario/productos/${id}/`, data);
        mutateProductos();
    }, [api, mutateProductos]);

    // --- Movimientos de Inventario ---
    const { data: movimientos, mutate: mutateMovimientos } = useSWR('/mi-negocio/inventario/movimientos/', fetcher);
    const createMovimiento = useCallback(async (data: Omit<MovimientoInventario, 'id' | 'producto_nombre' | 'almacen_nombre' | 'fecha'>) => {
        await api.post('/mi-negocio/inventario/movimientos/', data);
        mutateMovimientos();
        mutateProductos(); // Revalidar productos para actualizar stock
    }, [api, mutateMovimientos, mutateProductos]);

    return {
        // Categorías
        categorias,
        categoriasLoading: !categorias,
        createCategoria,

        // Almacenes
        almacenes,
        almacenesLoading: !almacenes,
        createAlmacen,

        // Productos
        productos,
        productosLoading: !productos && !productosError,
        productosError,
        createProducto,
        updateProducto,

        // Movimientos
        movimientos,
        movimientosLoading: !movimientos,
        createMovimiento,
    };
};
