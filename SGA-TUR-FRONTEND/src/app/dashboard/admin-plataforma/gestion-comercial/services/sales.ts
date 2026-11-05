
import { Opportunity, PipelineStage } from '../types/sales';

const API_BASE_URL = '/api/bff/sales';

// Function to get the JWT from local storage
const getAuthToken = (): string | null => {
    return localStorage.getItem('authToken');
};

interface ApiResponse<T> {
    data: T;
    meta?: {
        reason?: string;
    };
}

export const getOpportunities = async (): Promise<ApiResponse<Opportunity[]>> => {
    const token = getAuthToken();
    const response = await fetch(`${API_BASE_URL}/opportunities/`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        throw new Error('Failed to fetch opportunities');
    }

    // The BFF returns the data directly, so we wrap it in the expected structure
    const data = await response.json();
    if (Array.isArray(data) && data.length === 0) {
        return {
            data: [],
            meta: { reason: 'NO_DATA' }
        };
    }
    return { data };
};

export const moveOpportunity = async (opportunityId: number, newStage: PipelineStage): Promise<Opportunity> => {
    const token = getAuthToken();
    const response = await fetch(`${API_BASE_URL}/opportunities/${opportunityId}/move/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ stage: newStage }),
    });

    if (!response.ok) {
        throw new Error('Failed to move opportunity');
    }

    return await response.json();
};
