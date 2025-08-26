from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

app_name = 'usuarios' #para que os nomes das rotas agrupadas sejam reconhecidas e posam ser usadas

urlpatterns = [
    path('login/', login_view, name='login'), # Página de login
    path('cadastro/', cadastro, name='cadastro'), #pagina de cadastro
    path('principal/', principal, name='pag_principal'), # /principal → principal()
    path('criar-sala/', criar_sala, name='criar_sala'), #view para criar sala
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), #view para logout
]