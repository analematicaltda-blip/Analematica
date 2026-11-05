'use client';

export interface AuditEvent {
  id: string;
  timestamp: string;
 
  type:
    | 'VIEW_LOAD'
    | 'ACTION_ATTEMPT'
    | 'ACTION_PERMITTED'
    | 'ACTION_DENIED'
    | 'DATA_ERROR'
    | 'VOICE_INTENT_DETECTED'
    | 'VOICE_ACTION_CONFIRMED'
    | 'VOICE_ACTION_ABORTED';
 
  view: string;
  action?: string;
  details?: any;
  userRole: string;
  userEmail?: string;
  status: 'OK' | 'WARN' | 'ERROR' | 'INFO';
}

const MAX_LOGS = 100;

export const auditLogger = {
  log: (event: Omit<AuditEvent, 'id' | 'timestamp'>) => {
    if (typeof window === 'undefined') return;

    const fullEvent: AuditEvent = {
      ...event,
      id: Math.random().toString(36).substring(2, 11),
      timestamp: new Date().toISOString(),
    };

    // Log to console for dev visibility
    const color = event.status === 'ERROR' ? 'red' : event.status === 'WARN' ? 'orange' : 'blue';
    console.log(`%c[AUDIT] ${fullEvent.type} on ${fullEvent.view}: ${fullEvent.action || ''}`, `color: ${color}; font-weight: bold;`, event.details || '');

    // Persist in localStorage for visual audit within session
    try {
      const logsRaw = localStorage.getItem('frontend_audit_logs');
      const logs: AuditEvent[] = logsRaw ? JSON.parse(logsRaw) : [];

      logs.unshift(fullEvent);

      // Keep only last N logs
      const trimmedLogs = logs.slice(0, MAX_LOGS);
      localStorage.setItem('frontend_audit_logs', JSON.stringify(trimmedLogs));
    } catch (e) {
      console.error("Failed to persist audit log", e);
    }
  },

  getLogs: (): AuditEvent[] => {
    if (typeof window === 'undefined') return [];
    try {
      const logsRaw = localStorage.getItem('frontend_audit_logs');
      return logsRaw ? JSON.parse(logsRaw) : [];
    } catch (e) {
      return [];
    }
  },

  clear: () => {
    if (typeof window === 'undefined') return;
    localStorage.removeItem('frontend_audit_logs');
  }
};
