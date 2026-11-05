import httpClient from './index';

export interface SystemFlag {
    id: string;
    name: string;
    status: 'ACTIVE' | 'PAUSED' | 'LOCKED';
    description: string;
}

export interface AgentStatus {
    id: string;
    role: string;
    hierarchy: string;
    status: 'ACTIVE' | 'PAUSED' | 'KILLED';
    last_action: string;
    domain: string;
}

export const sovereigntyService = {
    getSystemStatus: () => httpClient.get('/admin/plataforma/status/'),

    // Agent Controls
    getAgents: () => httpClient.get<AgentStatus[]>('/admin/plataforma/agents/'),
    pauseAgent: (id: string) => httpClient.post(`/admin/plataforma/agents/${id}/pause/`),
    resumeAgent: (id: string) => httpClient.post(`/admin/plataforma/agents/${id}/resume/`),
    killAgent: (id: string) => httpClient.post(`/admin/plataforma/agents/${id}/kill/`),

    // Global Flags
    getFlags: () => httpClient.get<SystemFlag[]>('/admin/plataforma/flags/'),
    toggleFlag: (id: string, status: string) => httpClient.post(`/admin/plataforma/flags/${id}/toggle/`, { status }),

    // Emergency
    activateKillMode: (reason: string) => httpClient.post('/admin/plataforma/emergency/kill-mode/', { reason }),
    deactivateKillMode: () => httpClient.post('/admin/plataforma/emergency/restore/'),
};
