'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';

export interface TowerEvent {
  event_id: string;
  event_type: string;
  timestamp: string;
  entity_id: string;
  user_id: string;
  payload: any;
  severity: 'info' | 'warning' | 'critical' | 'fatal';
}

export const useWebSockets = () => {
  const { token, isAuthenticated } = useAuth();
  const [lastEvent, setLastEvent] = useState<TowerEvent | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (!isAuthenticated || !token) return;

    // Determinar URL del WebSocket (Protocolo ws o wss según el entorno)
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = process.env.NEXT_PUBLIC_WS_HOST || 'localhost:8000';
    const wsUrl = `${protocol}//${host}/ws/tower/?token=${token}`;

    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log('Tower WebSocket: Conexión establecida.');
      setIsConnected(true);
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLastEvent(data);
        console.log('Tower Event Received:', data);
      } catch (err) {
        console.error('Tower WebSocket: Error parseando mensaje', err);
      }
    };

    ws.current.onclose = (e) => {
      setIsConnected(false);
      console.log('Tower WebSocket: Conexión cerrada. Reintentando en 5s...', e.reason);
      reconnectTimeout.current = setTimeout(connect, 5000);
    };

    ws.current.onerror = (err) => {
      console.error('Tower WebSocket: Error detectado', err);
      ws.current?.close();
    };
  }, [token, isAuthenticated]);

  useEffect(() => {
    connect();
    return () => {
      if (ws.current) ws.current.close();
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
    };
  }, [connect]);

  return { lastEvent, isConnected };
};
