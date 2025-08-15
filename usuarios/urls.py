from django.urls import path
from .views import *
from . import views

app_name = 'usuarios' #para que os nomes das rotas agrupadas sejam reconhecidas e posam ser usadas

urlpatterns = [
    path('login/', login_view, name='login'), # Página de login
    path('cadastro/', cadastro, name='cadastro'), #pagina de cadastro
    path('principal/', principal, name='pag_principal'), # /principal → principal()
    path('criar-sala/', criar_sala, name='criar_sala'), #view para criar sala
    path('salas/', views.lista_salas, name='lista_salas'),
]