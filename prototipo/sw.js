const CACHE_NAME = 'smartresto-public-v1';
const APP_SHELL = [
  './index.html','./descubrir.html','./mercado.html','./menu-3d.html',
  './experiencias.html','./negocios.html','./ingresar.html','./registrarse.html',
  './nosotros.html','./como-funciona.html','./ayuda.html','./contacto.html',
  './terminos.html','./privacidad.html','./cookies.html','./accesibilidad.html','./comunidad.html','./offline.html','./ecosistema-demo.html',
  './assets/css/site.css','./assets/js/site.js','./assets/img/brand-mark.svg','./manifest.webmanifest'
];
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key.startsWith('smartresto-public-') && key !== CACHE_NAME).map(key => caches.delete(key)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.includes('/api/')) return;
  // Navigation: network first, then the cached shell page.
  if (request.mode === 'navigate') {
    event.respondWith(fetch(request).then(response => {
      if (response.ok) { const copy=response.clone(); caches.open(CACHE_NAME).then(cache=>cache.put(request,copy)); }
      return response;
    }).catch(async () => (await caches.match(request)) || (await caches.match('./offline.html')) || (await caches.match('./index.html'))));
    return;
  }
  // Versioned public assets: cache first, revalidate in the background.
  if (!(url.pathname.includes('/assets/') || url.pathname.endsWith('/manifest.webmanifest'))) return;
  event.respondWith(caches.match(request).then(cached => {
    const network = fetch(request).then(response => {
      if (response.ok) caches.open(CACHE_NAME).then(cache => cache.put(request,response.clone()));
      return response;
    });
    return cached || network;
  }));
});
