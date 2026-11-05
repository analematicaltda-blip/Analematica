import { OfflineQueue } from './OfflineQueue';

export const initSyncManager = () => {
  window.addEventListener('online', () => {
    console.log('SYSTEM: Connection restored. Processing queue...');
    OfflineQueue.process();
  });

  window.addEventListener('offline', () => {
    console.log('SYSTEM: Offline mode activated.');
  });
};
