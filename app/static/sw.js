
const CACHE_NAME = "smartresto-flask-v2";

const OFFLINE_URL = "/offline";

const PUBLIC_ASSETS = [
  "/static/assets/css/site.css",
  "/static/assets/img/brand-mark.svg"
];

// INSTALACIÓN
self.addEventListener("install", (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE_NAME);

      // La página offline es el recurso indispensable.
      await cache.add(OFFLINE_URL);

      // Los recursos visuales se intentan guardar individualmente.
      await Promise.allSettled(
        PUBLIC_ASSETS.map((asset) => cache.add(asset))
      );

      await self.skipWaiting();
    })()
  );
});

// ACTIVACIÓN
self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();

      await Promise.all(
        keys
          .filter(
            (key) =>
              key.startsWith("smartresto-flask-") &&
              key !== CACHE_NAME
          )
          .map((key) => caches.delete(key))
      );

      await self.clients.claim();
    })()
  );
});

// PETICIONES
self.addEventListener("fetch", (event) => {
  const request = event.request;

  if (request.method !== "GET") return;

  const url = new URL(request.url);

  // Solo recursos del mismo dominio.
  if (url.origin !== self.location.origin) return;

  // Nunca interceptar ni almacenar respuestas de la API.
  if (url.pathname.startsWith("/api/")) return;

  // NAVEGACIÓN: red primero, página offline como respaldo.
  if (request.mode === "navigate") {
    event.respondWith(
      (async () => {
        try {
          return await fetch(request);
        } catch (error) {
          const cache = await caches.open(CACHE_NAME);

          return (
            await cache.match(OFFLINE_URL)
          ) || new Response(
            "SmartResto no está disponible sin conexión.",
            {
              status: 503,
              headers: {
                "Content-Type": "text/plain; charset=utf-8"
              }
            }
          );
        }
      })()
    );

    return;
  }

  // RECURSOS ESTÁTICOS: caché primero.
  if (url.pathname.startsWith("/static/")) {
    event.respondWith(
      (async () => {
        const cache = await caches.open(CACHE_NAME);
        const cached = await cache.match(request);

        if (cached) {
          // Actualizar la caché sin bloquear la respuesta.
          fetch(request)
            .then((response) => {
              if (response.ok) {
                return cache.put(request, response);
              }
            })
            .catch(() => {});

          return cached;
        }

        try {
          const response = await fetch(request);

          if (response.ok) {
            await cache.put(request, response.clone());
          }

          return response;
        } catch (error) {
          return new Response("Recurso no disponible sin conexión.", {
            status: 503,
            headers: {
              "Content-Type": "text/plain; charset=utf-8"
            }
          });
        }
      })()
    );
  }
});
