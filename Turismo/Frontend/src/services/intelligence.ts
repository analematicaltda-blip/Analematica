import api from './api';

export interface StrategyProposal {
    id: string;
    domain: string;
    status: string;
    contexto_detectado: string;
    riesgo_actual: string;
    oportunidad_detectada: string;
    accion_sugerida: any;
    impacto_estimado: string;
    nivel_confianza: number;
    nivel_urgencia: string;
    nivel_riesgo: string;
    decision_level: number;
    created_at: string;
}

// Vía 3: Conversational Intelligence

export interface ConversationalIntent {
    id: string;
    conversation_id: string;
    message_id: string;
    tourist: string;
    tourist_name: string;
    intent: string;
    confidence_score: number;
    sentiment_score: number;
    detected_entities: any;
    created_at: string;
}

export interface ConversationalKPI {
    id: string;
    provider: string;
    provider_name: string;
    avg_response_time_seconds: number;
    response_rate: number;
    total_chats: number;
    missed_chats: number;
    period: string;
}

export const getStrategyProposals = async (): Promise<StrategyProposal[]> => {
    const response = await api.get('/admin/intelligence/proposals/');
    return response.data;
};

export const approveStrategyProposal = async (id: string, justification?: string) => {
    const response = await api.post(`/admin/intelligence/proposals/${id}/approve/`, {
        justificacion_humana: justification
    });
    return response.data;
};

export const executeStrategyProposal = async (id: string) => {
    const response = await api.post(`/admin/intelligence/proposals/${id}/execute/`);
    return response.data;
};

export const rejectStrategyProposal = async (id: string) => {
    const response = await api.post(`/admin/intelligence/proposals/${id}/reject/`);
    return response.data;
};

export const getConversationalIntents = async (): Promise<ConversationalIntent[]> => {
    const response = await api.get('/tourism/intelligence/intents/');
    return response.data?.results ?? response.data ?? [];
};

export const getConversationalKPIs = async (): Promise<ConversationalKPI[]> => {
    const response = await api.get('/tourism/intelligence/chat-kpis/');
    return response.data?.results ?? response.data ?? [];
};

export const getTourismForecast = async (destino: string, categoria: string, fecha: string) => {
    const response = await api.get('/tourism/intelligence/intelligence/forecast/', {
        params: { destino, categoria, fecha }
    });
    return response.data;
};

export const getEconomicImpact = async (destino: string, periodo: string) => {
    const response = await api.get('/tourism/intelligence/economic-impact/', {
        params: { destino, periodo }
    });
    return response.data;
};

export const getUnifiedDashboard = async (departmentId?: string, municipalityId?: string) => {
    const response = await api.get('/tourism/intelligence/dashboard/', {
        params: {
            department: departmentId,
            municipality: municipalityId
        }
    });
    return response.data;
};
