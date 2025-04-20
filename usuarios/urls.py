from django.urls import path
from .views import login_view, cadastro

app_name = 'usuarios' #para que os nomes das rotas agrupadas sejam reconhecidas e posam ser usadas

urlpatterns = [
    path('login/', login_view, name='login'), # Página de login
    path('cadastro/', cadastro, name='cadastro') #pagina de cadastro
]