/**
 * PHASE J: Advanced Offline PWA Support
 */
import { precacheAndRoute } from 'workbox-precaching';
import { registerRoute } from 'workbox-routing';
import { StaleWhileRevalidate, CacheFirst, NetworkFirst } from 'workbox-strategies';

// Precache static assets
// @ts-ignore
precacheAndRoute(self.__WB_MANIFEST || []);

// Dashboard Data: NetworkFirst (Ensures freshness, fallback to cache)
registerRoute(
  ({url}) => url.pathname.startsWith('/api/v1/'),
  new NetworkFirst({
    cacheName: 'api-responses',
  })
);

// Assets: CacheFirst
registerRoute(
  ({request}) => request.destination === 'image',
  new CacheFirst({
    cacheName: 'images',
  })
);

// PWA Background Sync for Transactions
// @ts-ignore
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-transactions') {
    // @ts-ignore
    event.waitUntil(processOfflineQueue());
  }
});

async function processOfflineQueue() {
    console.log("PWA: Background synchronization triggered.");
    // Implementation would call the SyncService from SDK
}
