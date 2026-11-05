import React, { useState, useEffect } from 'react';
import { Wifi, WifiOff, RefreshCcw } from 'lucide-react';

export const ConnectivityIndicator = () => {
  const [status, setStatus] = useState<'online' | 'offline' | 'syncing'>('online');

  useEffect(() => {
    const handleOnline = () => setStatus('online');
    const handleOffline = () => setStatus('offline');

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    if (!navigator.onLine) setStatus('offline');

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (status === 'online') return null;

  return (
    <div style={{
      position: 'fixed',
      bottom: '20px',
      right: '20px',
      padding: '12px 16px',
      borderRadius: '12px',
      backgroundColor: status === 'offline' ? '#ff0000' : '#0070f3',
      color: '#fff',
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
      zIndex: 1000,
    }}>
      {status === 'offline' ? (
        <>
          <WifiOff size={18} />
          <span>Modo Offline activo</span>
        </>
      ) : (
        <>
          <RefreshCcw size={18} className="animate-spin" />
          <span>Sincronizando datos...</span>
        </>
      )}
    </div>
  );
};
