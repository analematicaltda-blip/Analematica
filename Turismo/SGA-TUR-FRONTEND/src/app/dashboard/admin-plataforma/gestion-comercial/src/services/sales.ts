
import axios from 'axios';
import { Opportunity } from '../types'; // Assuming Opportunity will be defined in types.ts

const API_URL = '/api/bff/sales';
const AUTH_URL = '/api/bff/auth';

export const setAuthToken = (token: string | null) => {
    if (token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
        delete axios.defaults.headers.common['Authorization'];
    }
};

export const login = async (email, password) => {
    const response = await axios.post(`${AUTH_URL}/token/`, { email, password });
    return response.data;
};

export const getOpportunities = async (): Promise<{ data: Opportunity[], meta: { reason?: string } }> => {
    const response = await axios.get(`${API_URL}/opportunities/`);
    if (response.data.meta?.reason === 'NO_DATA') {
        console.warn('No opportunities found for this tenant.');
        return { data: [], meta: { reason: 'NO_DATA' } };
    }
    return response.data;
};

export const moveOpportunity = async (opportunityId: number, stage: string): Promise<Opportunity> => {
    const response = await axios.put(`${API_URL}/opportunities/${opportunityId}/move/`, { stage });
    return response.data;
};
