from django.shortcuts import render
from django.http import HttpResponse, FileResponse
import os
from django.conf import settings

def home(request):
    return render(request,'home.html')

def service_worker(request):
    """
    Serve o service worker na raiz do domínio (/sw.js).
    Isso é OBRIGATÓRIO para que o SW tenha escopo sobre todas as páginas.
    O arquivo deve estar em static/js/sw.js.
    """
    sw_path = os.path.join(settings.BASE_DIR, 'static', 'js', 'sw.js')
    response = FileResponse(open(sw_path, 'rb'), content_type='application/javascript')
    # O header Service-Worker-Allowed expande o escopo se necessário
    response['Service-Worker-Allowed'] = '/'
    # Não cachear o próprio SW para garantir atualizações
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response