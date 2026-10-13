/* VeristasOS Service Worker — PWA offline support */
const CACHE_NAME = 'veristasos-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/app.js',
  '/style.css',
  '/i18n.js',
  '/manifest.json',
];

// Install: cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// Activate: clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// Fetch: network-first strategy for API, cache-first for static assets
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Always fetch API calls from network
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/health')) {
    event.respondWith(fetch(request).catch(() => new Response(
      JSON.stringify({ error: 'Offline — please check your connection.' }),
      { headers: { 'Content-Type': 'application/json' } }
    )));
    return;
  }

  // Cache-first for static assets
  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) return cached;
      return fetch(request).then((response) => {
        if (response && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
        }
        return response;
      }).catch(() => caches.match('/'));
    })
  );
});
