import httpClient from './httpClient';

export interface AutonomousAction {
    id: string;
    name: string;
    domain: string;
    description: string;
    autonomy_level: number;
    max_daily_executions: number;
    max_financial_impact: string;
    is_active: boolean;
    policy_reference: string;
}

export interface AutonomousExecutionLog {
    id: string;
    action_name: string;
    timestamp: string;
    explanation: string;
    data_points: any;
    policy_applied: string;
    result_status: string;
    was_interrupted: boolean;
}

export interface AutonomyControl {
    domain: string | null;
    is_enabled: boolean;
    reason: string;
}

export const autonomyService = {
    getActions: () => httpClient.get<AutonomousAction[]>('/admin/optimization/actions/'),
    getLogs: () => httpClient.get<AutonomousExecutionLog[]>('/admin/optimization/logs/'),
    getControls: () => httpClient.get<AutonomyControl[]>('/admin/optimization/controls/'),

    toggleGlobalKillSwitch: (enabled: boolean, reason: string) =>
        httpClient.post('/admin/optimization/controls/global_kill_switch/', { enabled, reason }),

    triggerAction: (actionId: string, parameters: any) =>
        httpClient.post(`/admin/optimization/actions/${actionId}/trigger/`, { parameters })
};
