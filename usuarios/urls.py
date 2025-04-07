from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'), #pagina inicial
    path('cadastro/', views.cadastro, name='cadastro') #pagina de cadastro
]