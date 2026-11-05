import api from './api';

export interface OptimizationProposal {
    id: string;
    domain: string;
    status: string;
    hallazgo: string;
    propuesta_ajuste: string;
    parametros_cambio: any;
    impacto_esperado: string;
    created_at: string;
}

export const getOptimizationProposals = async (): Promise<OptimizationProposal[]> => {
    const response = await api.get('/admin/optimization/proposals/');
    return response.data.results || response.data;
};

export const applyOptimization = async (id: string, justification?: string) => {
    const response = await api.post(`/admin/optimization/proposals/${id}/apply/`, {
        justificacion: justification
    });
    return response.data;
};

export const rollbackOptimization = async (id: string) => {
    const response = await api.post(`/admin/optimization/proposals/${id}/rollback/`);
    return response.data;
};

export const runOptimizationCycle = async () => {
    const response = await api.post('/admin/optimization/proposals/run_cycle/');
    return response.data;
};
