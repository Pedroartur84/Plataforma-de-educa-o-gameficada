const CACHE_NAME = 'player-v1';
const STATIC_ASSETS = [
  '/',
  '/usuarios/principal/',
  '/static/styles/style.css',
  '/static/js/chat_sala.js',
  '/static/manifest.json',
  '/static/icons/maskable_icon_x192.png',
  '/static/icons/maskable_icon_x512.png',
];

// Instalação: faz cache dos arquivos estáticos
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// Ativação: limpa caches antigos
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch: tenta rede primeiro, cai no cache se offline
self.addEventListener('fetch', (event) => {
  // Ignorar requisições que não são GET ou são da API do Django
  if (event.request.method !== 'GET') return;
  if (event.request.url.includes('/admin/')) return;

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Guarda cópia no cache se for resposta válida
        if (response && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});