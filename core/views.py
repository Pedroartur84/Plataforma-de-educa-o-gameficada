from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from django.conf import settings
import os
import re
import mimetypes
import json
import logging
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)


def home(request):
    return render(request, 'home.html')


def _find_icon_sources():
    """Retorna uma lista de (dir_path, url_prefix) candidatos em ordem de prioridade."""
    base = settings.BASE_DIR
    base_url = ''
    if hasattr(settings, 'STATIC_URL') and settings.STATIC_URL:
        base_url = settings.STATIC_URL
    else:
        base_url = '/static/'
    if not base_url.endswith('/'):
        base_url = base_url + '/'

    candidates = []
    # prioridade: static/pwa-icons
    candidates.append((os.path.join(base, 'static', 'pwa-icons'), f"{base_url}pwa-icons/"))
    # fallback: static/img
    candidates.append((os.path.join(base, 'static', 'img'), f"{base_url}img/"))
    # fallback: fotos_para_app (legacy)
    candidates.append((os.path.join(base, 'fotos_para_app'), f"{base_url}fotos_para_app/"))
    return candidates


def manifest(request):
    """Gera dinamicamente o `manifest.json` priorizando `static/pwa-icons`.

    - Detecta arquivos .png/.jpg/.jpeg
    - Reconhece `maskable` no nome e adiciona `purpose: "maskable"`
    - Preenche `sizes` a partir do nome do arquivo (ex: 192x192)
    - Adiciona campos modernos: scope, orientation, screenshots se presentes
    """
    base_url = request.build_absolute_uri('/')[:-1]
    icons = []
    screenshots = []

    found = False
    candidates = _find_icon_sources()
    for dir_path, url_prefix in candidates:
        if os.path.isdir(dir_path):
            try:
                for fname in sorted(os.listdir(dir_path)):
                    if not fname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        continue
                    found = True
                    low = fname.lower()
                    sizes_match = re.search(r"(\d+x\d+)", low)
                    sizes = sizes_match.group(1) if sizes_match else "any"
                    purpose = 'maskable' if 'maskable' in low else 'any'
                    mime, _ = mimetypes.guess_type(fname)
                    if not mime:
                        mime = 'image/png'
                    src = f"{base_url}{url_prefix}{fname}"
                    icon_entry = {
                        'src': src,
                        'type': mime,
                        'sizes': sizes,
                    }
                    if purpose != 'any':
                        icon_entry['purpose'] = purpose
                    icons.append(icon_entry)
                # procurar screenshots em subpasta screenshots/
                screenshots_dir = os.path.join(dir_path, 'screenshots')
                if os.path.isdir(screenshots_dir):
                    for sname in sorted(os.listdir(screenshots_dir)):
                        if sname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                            smime, _ = mimetypes.guess_type(sname)
                            ssizes = re.search(r"(\d+x\d+)", sname.lower())
                            screenshots.append({
                                'src': f"{base_url}{url_prefix}screenshots/{sname}",
                                'type': smime or 'image/png',
                                'sizes': ssizes.group(1) if ssizes else 'any'
                            })
            except FileNotFoundError:
                continue
        if found:
            break

    data = {
        'name': getattr(settings, 'PWA_APP_NAME', 'Plataforma de Educação'),
        'short_name': getattr(settings, 'PWA_SHORT_NAME', 'Plataforma'),
        'start_url': getattr(settings, 'PWA_START_URL', '/'),
        'scope': getattr(settings, 'PWA_SCOPE', '/'),
        'display': getattr(settings, 'PWA_DISPLAY', 'standalone'),
        'background_color': getattr(settings, 'PWA_BACKGROUND_COLOR', '#1A1A1A'),
        'theme_color': getattr(settings, 'PWA_THEME_COLOR', '#FFC107'),
        'orientation': getattr(settings, 'PWA_ORIENTATION', 'portrait'),
        'prefer_related_applications': False,
        'related_applications': [],
        'icons': icons,
    }
    if screenshots:
        data['screenshots'] = screenshots

    return JsonResponse(data)


def service_worker(request):
    """Retorna um service worker básico porém robusto em JS.

    - Precache de rotas principais
    - Cache-first para assets estáticos
    - Network-first para APIs
    - Fallback para /offline/
    """
    # construir lista de precache (URLs relativos)
    base_url = ''
    sw_precache = [
        '/',
        '/offline/',
        '/manifest.json',
        '/static/js/pwa-register.js',
    ]

    # incluir ícones pwa no precache (se existirem)
    candidates = _find_icon_sources()
    for dir_path, url_prefix in candidates:
        if os.path.isdir(dir_path):
            for fname in sorted(os.listdir(dir_path)):
                if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    sw_precache.append(f"{url_prefix}{fname}")
            # screenshots
            screenshots_dir = os.path.join(dir_path, 'screenshots')
            if os.path.isdir(screenshots_dir):
                for sname in sorted(os.listdir(screenshots_dir)):
                    if sname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        sw_precache.append(f"{url_prefix}screenshots/{sname}")
            break

    # garantir URLs únicas
    sw_precache = list(dict.fromkeys(sw_precache))

    sw_js = f"""const CACHE_PREFIX = 'plataforma-pwa-';
const CACHE_VERSION = 'v1';
const PRECACHE = {json.dumps(sw_precache)};
const RUNTIME = CACHE_PREFIX + CACHE_VERSION + '-runtime';

self.addEventListener('install', event => {{
  event.waitUntil(
    caches.open(CACHE_PREFIX + CACHE_VERSION).then(cache => cache.addAll(PRECACHE))
  );
  self.skipWaiting();
}});

self.addEventListener('activate', event => {{
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => !k.startsWith(CACHE_PREFIX + CACHE_VERSION)).map(k => caches.delete(k))
    ))
  );
  self.clients.claim();
}});

self.addEventListener('fetch', event => {{
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // Network-first for API calls
  if (url.pathname.includes('/api/') || url.pathname.includes('sala_messages') || url.pathname.includes('missao_messages')) {{
    event.respondWith(
      fetch(event.request).then(resp => {{
        const copy = resp.clone();
        caches.open(RUNTIME).then(cache => cache.put(event.request, copy));
        return resp;
      }}).catch(() => caches.match(event.request))
    );
    return;
  }}

  // Navigation - try network, fallback to offline page
  if (event.request.mode === 'navigate') {{
    event.respondWith(
      fetch(event.request).then(resp => {{
        caches.open(RUNTIME).then(cache => cache.put(event.request, resp.clone()));
        return resp;
      }}).catch(() => caches.match('/offline/'))
    );
    return;
  }}

  // Cache-first for static assets (css, js, images)
  if (url.pathname.startsWith('/static/') || url.pathname.match(/\.(?:png|jpg|jpeg|gif|svg|css|js|webp)$/)) {{
    event.respondWith(
      caches.match(event.request).then(cached => cached || fetch(event.request).then(resp => {{
        caches.open(RUNTIME).then(cache => cache.put(event.request, resp.clone()));
        return resp;
      }}).catch(() => caches.match('/offline/')))
    );
    return;
  }}

  // Default: network-first
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
}});

self.addEventListener('message', event => {{
  if (event.data && event.data.type === 'SKIP_WAITING') {{
    self.skipWaiting();
  }}
}});
"""

    return HttpResponse(sw_js, content_type='application/javascript')


def pwa_icon(request, name):
    """Serve ícones priorizando `static/pwa-icons`, depois `static/img`, depois `fotos_para_app`."""
    safe_name = os.path.basename(name)
    candidates = [
        os.path.join(settings.BASE_DIR, 'static', 'pwa-icons', safe_name),
        os.path.join(settings.BASE_DIR, 'static', 'img', safe_name),
        os.path.join(settings.BASE_DIR, 'fotos_para_app', safe_name),
    ]
    for path in candidates:
        if os.path.exists(path):
            mime, _ = mimetypes.guess_type(path)
            return FileResponse(open(path, 'rb'), content_type=mime or 'application/octet-stream')
    raise Http404()
