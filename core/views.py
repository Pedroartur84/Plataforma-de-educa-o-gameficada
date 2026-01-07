from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from django.conf import settings
import os


def home(request):
    return render(request, 'home.html')


def manifest(request):
    """Retorna o manifest.json. Prioriza arquivos em `static/pwa-icons`, senão usa `fotos_para_app`.

    Observação: execute `python manage.py copy_pwa_icons` para copiar PNGs para `static/pwa-icons`.
    """
    base_url = request.build_absolute_uri('/')[:-1]
    icons = []
    # Preferir ícones copiados para static/img
    static_icons_dir = os.path.join(settings.BASE_DIR, 'static', 'img')
    source_dir = None
    if os.path.isdir(static_icons_dir):
        source_dir = static_icons_dir
        url_base = (settings.STATIC_URL or '/static/')
        if not url_base.endswith('/'):
            url_base = url_base + '/'
        url_prefix = f"{base_url}{url_base}img/"
    else:
        source_dir = os.path.join(settings.BASE_DIR, 'fotos_para_app')
        url_prefix = f"{base_url}/pwa-icon/"

    try:
        for fname in os.listdir(source_dir):
            if fname.lower().endswith('.png'):
                icons.append({
                    "src": f"{url_prefix}{fname}",
                    "type": "image/png",
                    "sizes": fname.replace('.png', '')
                })
    except FileNotFoundError:
        icons = []

    data = {
        "name": "Plataforma de Educação",
        "short_name": "Plataforma",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#1A1A1A",
        "theme_color": "#FFC107",
        "icons": icons,
    }
    return JsonResponse(data)


def service_worker(request):
    """Retorna o JavaScript do service worker."""
    sw_js = (
        "const CACHE_NAME = 'plataforma-pwa-v1';\n"
        "const OFFLINE_URLS = ['/','/static/styles/style.css'];\n"

        "self.addEventListener('install', event => {\n"
        "  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(OFFLINE_URLS)));\n"
        "  self.skipWaiting();\n"
        "});\n"

        "self.addEventListener('activate', event => {\n"
        "  event.waitUntil(caches.keys().then(keys => Promise.all(keys.map(key => {\n"
        "    if (key !== CACHE_NAME) return caches.delete(key);\n"
        "  }))));\n"
        "  self.clients.claim();\n"
        "});\n"

        "self.addEventListener('fetch', event => {\n"
        "  if (event.request.method !== 'GET') return;\n"
        "  event.respondWith(caches.match(event.request).then(resp => {\n"
        "    return resp || fetch(event.request).then(fetchResp => {\n"
        "      return caches.open(CACHE_NAME).then(cache => {\n"
        "        try { cache.put(event.request, fetchResp.clone()); } catch(e) {}\n"
        "        return fetchResp;\n"
        "      });\n"
        "    }).catch(() => caches.match('/'))\n"
        "  }));\n"
        "});\n"
    )
    return HttpResponse(sw_js, content_type='application/javascript')


def pwa_icon(request, name):
    icons_dir = os.path.join(settings.BASE_DIR, 'fotos_para_app')
    safe_name = os.path.basename(name)
    path = os.path.join(icons_dir, safe_name)
    if not os.path.exists(path):
        raise Http404()
    return FileResponse(open(path, 'rb'), content_type='image/png')
