from . import views
from django.urls import path

app_name = 'usuarios' #para que os nomes das rotas agrupadas sejam reconhecidas e posam ser usadas

urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro') #pagina de cadastro
]