const CACHE_NAME = 'sga-cd-pwa-v4-landing';
const urlsToCache = [
  '/',
  'index.html',
  'app.html',
  'login.html',
  'register.html',
  '404.html',
  'offline.html',
  'css/style.css',
  'css/app.css',
  'css/sky-theme.css',
  'js/main.js',
  'js/components/modern_carousel.js',
  'assets/images/carousel-fallback.svg',
  'js/app.js',
  'js/navigation.js',
  'js/views/alumno.js',
  'js/register.js'
];

// Activate a completed release without leaving open clients on obsolete CSS/JS.
self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    await cache.addAll(urlsToCache);
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names.filter(name => name.startsWith('sga-cd-') && name !== CACHE_NAME).map(name => caches.delete(name)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);
  // Never store API, authenticated responses, writes or third-party traffic.
  if (request.method !== 'GET' || url.origin !== self.location.origin ||
      url.pathname.startsWith('/api/') || request.headers.has('Authorization')) return;

  const freshFirst = request.mode === 'navigate' ||
    ['script', 'style'].includes(request.destination) || /\.(?:html|js|css)$/.test(url.pathname);
  event.respondWith((async () => {
    const cache = await caches.open(CACHE_NAME);
    if (!freshFirst) {
      const cached = await cache.match(request);
      if (cached) return cached;
    }
    try {
      const response = await fetch(request);
      if (response.ok) await cache.put(request, response.clone());
      return response;
    } catch (error) {
      const cached = await cache.match(request);
      if (cached) return cached;
      if (request.mode === 'navigate' || request.headers.get('accept')?.includes('text/html')) {
        const fallback = await cache.match('offline.html');
        if (fallback) return fallback;
      }
      return Response.error();
    }
  })());
});
