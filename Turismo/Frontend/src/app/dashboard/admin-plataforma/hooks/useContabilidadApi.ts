import useSWR from 'swr';
import { useApi } from '@/services/api';
import { useCallback } from 'react';

export const useContabilidadApi = () => {
    const { api } = useApi();

    // --- Cost Centers ---
    const { data: costCenters, error: costCentersError, mutate: mutateCostCenters } = useSWR('/mi-negocio/contabilidad/cost-centers/', async (url: string) => {
        const response = await api.get(url);
        return response.data;
    });

    const createCostCenter = useCallback(async (data: { code: string; name: string }) => {
        const response = await api.post('/mi-negocio/contabilidad/cost-centers/', data);
        mutateCostCenters(); // Revalidar datos locales
        return response.data;
    }, [api, mutateCostCenters]);

    const updateCostCenter = useCallback(async (id: number, data: { code: string; name: string }) => {
        const response = await api.put(`/mi-negocio/contabilidad/cost-centers/${id}/`, data);
        mutateCostCenters();
        return response.data;
    }, [api, mutateCostCenters]);

    const deleteCostCenter = useCallback(async (id: number) => {
        await api.delete(`/mi-negocio/contabilidad/cost-centers/${id}/`);
        mutateCostCenters();
    }, [api, mutateCostCenters]);


    // --- Chart of Accounts (Read-only) ---
    const { data: chartOfAccounts, error: chartOfAccountsError } = useSWR('/mi-negocio/contabilidad/chart-of-accounts/', async (url: string) => {
        const response = await api.get(url);
        return response.data;
    });

    // --- Journal Entries ---
    const { data: journalEntries, error: journalEntriesError, mutate: mutateJournalEntries } = useSWR('/mi-negocio/contabilidad/journal-entries/', async (url: string) => {
        const response = await api.get(url);
        return response.data;
    });

    const createJournalEntry = useCallback(async (data: any) => {
        const response = await api.post('/mi-negocio/contabilidad/journal-entries/', data);
        mutateJournalEntries();
        return response.data;
    }, [api, mutateJournalEntries]);


    return {
        // Cost Centers
        costCenters,
        costCentersLoading: !costCenters && !costCentersError,
        costCentersError,
        createCostCenter,
        updateCostCenter,
        deleteCostCenter,

        // Chart of Accounts
        chartOfAccounts,
        chartOfAccountsLoading: !chartOfAccounts && !chartOfAccountsError,
        chartOfAccountsError,

        // Journal Entries
        journalEntries,
        journalEntriesLoading: !journalEntries && !journalEntriesError,
        journalEntriesError,
        createJournalEntry,
    };
};
