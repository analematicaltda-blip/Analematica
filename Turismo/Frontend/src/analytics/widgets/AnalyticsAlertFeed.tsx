'use client';

import React from 'react';
import { FiAlertTriangle, FiInfo, FiCheckCircle } from 'react-icons/fi';

export interface AlertNotification {
  id: string;
  type: 'warning' | 'info' | 'success' | 'error';
  title: string;
  message: string;
}

export const AnalyticsAlertFeed = ({ alerts }: { alerts: AlertNotification[] }) => {
  return (
    <div className="space-y-4">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className="p-4 rounded-xl bg-[var(--background-card)] border border-[var(--border-default)] shadow-sm hover:shadow-md transition-all flex gap-4"
        >
          <div className={`mt-1 ${
            alert.type === 'warning' ? 'text-amber-500' :
            alert.type === 'error' ? 'text-rose-500' :
            alert.type === 'success' ? 'text-emerald-500' : 'text-blue-500'
          }`}>
            {alert.type === 'warning' && <FiAlertTriangle size={18} />}
            {alert.type === 'info' && <FiInfo size={18} />}
            {alert.type === 'success' && <FiCheckCircle size={18} />}
            {alert.type === 'error' && <FiAlertTriangle size={18} />}
          </div>
          <div>
            <h4 className="text-xs font-black text-[var(--text-primary)] uppercase tracking-tight">{alert.title}</h4>
            <p className="text-[10px] text-[var(--text-muted)] mt-1">{alert.message}</p>
          </div>
        </div>
      ))}
      {alerts.length === 0 && (
        <div className="py-12 text-center text-[var(--text-muted)] italic text-xs">
          No hay alertas activas en este periodo.
        </div>
      )}
    </div>
  );
};
