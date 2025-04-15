from . import views
from django.urls import path

app_name = 'usuarios' #para que os nomes das rotas agrupadas sejam reconhecidas e posam ser usadas

urlpatterns = [
    path('login/', views.login_view, name='login'), # Página de login
     #pagina de cadastro
]