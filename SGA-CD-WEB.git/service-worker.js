const CACHE_NAME = 'sga-cd-pwa-v2';
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
  'js/main.js',
  'js/app.js',
  'js/navigation.js',
  'js/views/alumno.js',
  'js/register.js'
];

// Install a service worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Cache and return requests with offline fallback
self.addEventListener('fetch', event => {
  // Only handle GET requests for offline caching
  if (event.request.method !== 'GET') {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        if (response) {
          return response;
        }
        return fetch(event.request).catch(function() {
          // If network fetch fails and request is for an HTML page, return offline.html
          if (event.request.headers.get('accept') && event.request.headers.get('accept').includes('text/html')) {
            return caches.match('offline.html');
          }
        });
      })
  );
});

// Update a service worker
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
