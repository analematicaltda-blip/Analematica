import useSWR from 'swr';
import { useApi } from '@/services/api';
import { useCallback } from 'react';

// --- Tipos de Datos ---
interface CuentaBancaria {
    id: number;
    banco: string;
    numero_cuenta: string;
    tipo_cuenta: string;
    saldo_actual: string;
    titular: string;
}
interface TransaccionBancaria {
    id: number;
    cuenta: number;
    fecha: string;
    tipo: string;
    monto: string;
    descripcion: string;
}

export const useFinancieraApi = () => {
    const { api } = useApi();
    const fetcher = (url: string) => api.get(url).then(res => res.data);

    // --- Reportes ---
    const { data: reporteIngresosGastos, error: reporteError } = useSWR('/v1/mi-negocio/financiera/reporte-ingresos-gastos/', fetcher);

    // --- Cuentas Bancarias ---
    const { data: cuentas, error: cuentasError, mutate: mutateCuentas } = useSWR('/v1/mi-negocio/financiera/cuentas-bancarias/', fetcher);
    const createCuenta = useCallback(async (data: Omit<CuentaBancaria, 'id' | 'saldo_actual'>) => {
        await api.post('/v1/mi-negocio/financiera/cuentas-bancarias/', data);
        mutateCuentas();
    }, [api, mutateCuentas]);

    // --- Transacciones Bancarias ---
    const { data: transacciones, mutate: mutateTransacciones } = useSWR('/v1/mi-negocio/financiera/transacciones-bancarias/', fetcher);
    const createTransaccion = useCallback(async (data: Omit<TransaccionBancaria, 'id'>) => {
        await api.post('/v1/mi-negocio/financiera/transacciones-bancarias/', data);
        mutateTransacciones();
        mutateCuentas(); // Revalidar cuentas para actualizar saldos
    }, [api, mutateTransacciones, mutateCuentas]);

    return {
        // Cuentas Bancarias
        cuentas,
        cuentasLoading: !cuentas && !cuentasError,
        cuentasError,
        createCuenta,

        // Transacciones Bancarias
        transacciones,
        transaccionesLoading: !transacciones,
        createTransaccion,

        // Reportes
        reporteIngresosGastos,
        reporteLoading: !reporteIngresosGastos && !reporteError,
        reporteError,
    };
};
