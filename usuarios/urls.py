from django.urls import path, reverse_lazy
from .views import *
from . import views
from django.contrib.auth import views as auth_views

app_name = 'usuarios' #para que os nomes das rotas agrupadas sejam reconhecidas e posam ser usadas

urlpatterns = [
    path('login/', login_view, name='login'), # Página de login
    path('cadastro/', cadastro, name='cadastro'), #pagina de cadastro
    path('ativar/<uidb64>/<token>/', views.ativar, name='ativar'),
    path('principal/', principal, name='pag_principal'), # /principal → principal()
    path('criar-sala/', criar_sala, name='criar_sala'), #view para criar sala
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), #view para logout
    path('minhas-salas/', views.minhas_salas, name='minhas_salas'),  # Nova view para listar salas do usuário
    path('sala-virtual/<int:sala_id>/', views.sala_virtual, name='sala_virtual'),  # Nova view para sala virtual
    path('sala/<int:sala_id>/messages/', views.sala_messages, name='sala_messages'),
    path('detalhe-sala/<int:sala_id>/', views.detalhe_sala, name='detalhe_sala'),  # Nova view para detalhes da sala
    path('chat-missao/<int:missao_id>/', views.chat_missao, name='chat_missao'),  # Nova view para chat e missõess
    path('missao/<int:missao_id>/messages/', views.missao_messages, name='missao_messages'),
    path('postar-missao/<int:sala_id>/', views.postar_missao, name='postar_missao'),
    path('missoes/', views.missoes, name='missoes'),  # Nova view para listar missões do usuário
    path('ranking/', views.ranking, name='ranking'),  # Nova view para o ranking global
    path('configuracoes/', views.configuracoes, name='configuracoes'),  # Nova view para configurações do usuário
    path('painel-adm/', views.painel_adm, name='painel_adm'),  # Nova view para admin
    path('perfil/', perfil, name='perfil'),  # Editar perfil do usuário
    
    # Novas funcionalidades de sala
    path('sala/<int:sala_id>/atribuir-professor/', views.atribuir_professor, name='atribuir_professor'),
    path('sala/<int:sala_id>/deixar-professor/', views.deixar_de_ser_professor, name='deixar_professor'),
    path('sala/<int:sala_id>/sair/', views.sair_da_sala, name='sair_sala'),
    
    # referente a funcionalidade de titulos
    path('titulos/', views.listar_titulos, name='listar_titulos'),
    path('criar-titulo-global/', views.criar_titulo_global, name='criar_titulo_global'),
    path('criar-titulo-sala/<int:sala_id>/', views.criar_titulo_sala, name='criar_titulo_sala'),
    path('excluir-titulo/<int:titulo_id>/', views.excluir_titulo, name='excluir_titulo'),
    # Rotas para reset de senha (views nativas do Django)
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url=reverse_lazy('usuarios:password_reset_done')
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url=reverse_lazy('usuarios:password_reset_complete')
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
]