from django.urls import path
from . import views

app_name = 'cursos' #para que os nomes das rotas agrupadas sejam reconhecidas e posam ser usadas

urlpatterns = [
    # ==============================
    # URLS ANTIGAS (compatibilidade)
    # ==============================
    path('', views.lista_cursos, name='lista_cursos'),  # Redireciona para trilhas
    path('sala/<int:sala_id>/', views.detalhe_curso, name='detalhe_curso'),
    path('aula/<int:aula_id>/concluir/', views.marcar_aula_concluida, name='marcar_aula_concluida'),
    
    # ==============================
    # NOVO SISTEMA DE TRILHAS
    # ==============================
    
    # Listagem e navegação
    path('trilhas/', views.lista_trilhas, name='lista_trilhas'),
    path('trilha/<int:trilha_id>/', views.detalhe_trilha, name='detalhe_trilha'),
    path('conteudo/<int:conteudo_id>/', views.visualizar_conteudo, name='visualizar_conteudo'),
    
    # Criação (professores)
    path('sala/<int:sala_id>/criar-trilha/', views.criar_trilha, name='criar_trilha'),
    path('trilha/<int:trilha_id>/criar-modulo/', views.criar_modulo, name='criar_modulo'),
    path('modulo/<int:modulo_id>/adicionar-conteudo/', views.adicionar_conteudo, name='adicionar_conteudo'),
    
    # Exclusão (professores)
    path('conteudo/<int:conteudo_id>/excluir/', views.excluir_conteudo, name='excluir_conteudo'),
]