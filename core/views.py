from django.shortcuts import render
from django.http import HttpResponse, FileResponse
import os
from django.conf import settings

def home(request):
    return render(request,'home.html')

def service_worker(request):
    sw_path = os.path.join(settings.BASE_DIR, 'static', 'js', 'sw.js')
    return FileResponse(open(sw_path, 'rb'), content_type='application/javascript')