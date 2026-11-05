"use client";

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';
import { FiBell, FiCheck } from 'react-icons/fi';
import Link from 'next/link';

interface Notificacion {
  id: number;
  mensaje: string;
  leido: boolean;
  fecha_creacion: string;
  url?: string;
}

const NotificationBell = () => {
  const { user, token } = useAuth();
  const [notifications, setNotifications] = useState<Notificacion[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  const apiClient = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
    headers: { 'Authorization': `Token ${token}` },
  });

  useEffect(() => {
    if (user && token) {
      const fetchNotifications = () => {
        apiClient.get('/notificaciones/')
          .then(response => {
            const data = response.data.results || response.data;
            setNotifications(data);
            setUnreadCount(data.filter((n: Notificacion) => !n.leido).length);
          })
          .catch(err => {
            // Silently fail on background refresh to avoid interrupting the user.
          });
      };

      fetchNotifications();
      const interval = setInterval(fetchNotifications, 60000); // Recargar cada minuto

      return () => clearInterval(interval);
    }
  }, [user, token]);

  const handleMarkAllAsRead = async () => {
    try {
      await apiClient.post('/notificaciones/marcar-como-leidas/');
      setNotifications(notifications.map(n => ({ ...n, leido: true })));
      setUnreadCount(0);
    } catch (error) {
      // Silently fail, or show a non-intrusive toast notification
    }
  };

  if (!user) return null;

  return (
    <div className="relative">
      <button onClick={() => setIsOpen(!isOpen)} className="relative text-gray-600 hover:text-blue-600">
        <FiBell className="h-6 w-6" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-xs text-white">
            {unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl z-20">
          <div className="p-4 flex justify-between items-center border-b">
            <h3 className="font-semibold text-gray-800">Notificaciones</h3>
            {unreadCount > 0 && (
              <button onClick={handleMarkAllAsRead} className="text-xs text-blue-600 hover:underline">
                Marcar todas como leídas
              </button>
            )}
          </div>
          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <p className="text-center text-gray-500 py-6">No tienes notificaciones.</p>
            ) : (
              notifications.map(notif => (
                <Link key={notif.id} href={notif.url || '#'} legacyBehavior>
                  <a className={`block px-4 py-3 hover:bg-gray-100 ${!notif.leido ? 'bg-blue-50' : ''}`}>
                    <p className="text-sm text-gray-700">{notif.mensaje}</p>
                    <p className="text-xs text-gray-400 mt-1">{new Date(notif.fecha_creacion).toLocaleString()}</p>
                  </a>
                </Link>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationBell;