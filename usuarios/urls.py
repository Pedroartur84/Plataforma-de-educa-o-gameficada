from django.urls import path
from .views import *
from . import views
from django.contrib.auth import views as auth_views

app_name = 'usuarios' #para que os nomes das rotas agrupadas sejam reconhecidas e posam ser usadas

urlpatterns = [
    path('login/', login_view, name='login'), # Página de login
    path('cadastro/', cadastro, name='cadastro'), #pagina de cadastro
    path('principal/', principal, name='pag_principal'), # /principal → principal()
    path('criar-sala/', criar_sala, name='criar_sala'), #view para criar sala
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), #view para logout
    path('minhas-salas/', views.minhas_salas, name='minhas_salas'),  # Nova view para listar salas do usuário
    path('sala-virtual/<int:sala_id>/', views.sala_virtual, name='sala_virtual'),  # Nova view para sala virtual
    path('detalhe-sala/<int:sala_id>/', views.detalhe_sala, name='detalhe_sala'),  # Nova view para detalhes da sala
    path('chat-missao/<int:missao_id>/', views.chat_missao, name='chat_missao'),  # Nova view para chat e missõess
    path('postar-missao/<int:sala_id>/', views.postar_missao, name='postar_missao'),
    path('missoes/', views.missoes, name='missoes'),  # Nova view para listar missões do usuário
    path('ranking/', views.ranking, name='ranking'),  # Nova view para o ranking global
    path('configuracoes/', views.configuracoes, name='configuracoes'),  # Nova view para configurações do usuário
    path('painel-adm/', views.painel_adm, name='painel_adm'),  # Nova view para admin
]