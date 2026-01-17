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
    
    # ==============================
    # GERENCIAMENTO DE TRILHAS (Professor)
    # ==============================
    
    # Criar, editar, excluir e reordenar trilhas
    path('sala/<int:sala_id>/criar-trilha/', views.criar_trilha, name='criar_trilha'),
    path('trilha/<int:trilha_id>/editar/', views.editar_trilha, name='editar_trilha'),
    path('trilha/<int:trilha_id>/excluir/', views.excluir_trilha, name='excluir_trilha'),
    path('sala/<int:sala_id>/reordenar-trilhas/', views.reordenar_trilhas, name='reordenar_trilhas'),
    
    # ==============================
    # GERENCIAMENTO DE MÓDULOS (Professor)
    # ==============================
    
    path('trilha/<int:trilha_id>/criar-modulo/', views.criar_modulo, name='criar_modulo'),
    path('modulo/<int:modulo_id>/editar/', views.editar_modulo, name='editar_modulo'),
    path('modulo/<int:modulo_id>/excluir/', views.excluir_modulo, name='excluir_modulo'),
    path('trilha/<int:trilha_id>/reordenar-modulos/', views.reordenar_modulos, name='reordenar_modulos'),
    
    # ==============================
    # GERENCIAMENTO DE CONTEÚDOS (Professor)
    # ==============================
    
    path('modulo/<int:modulo_id>/adicionar-conteudo/', views.adicionar_conteudo, name='adicionar_conteudo'),
    path('conteudo/<int:conteudo_id>/editar/', views.editar_conteudo, name='editar_conteudo'),
    path('conteudo/<int:conteudo_id>/excluir/', views.excluir_conteudo, name='excluir_conteudo'),
    path('modulo/<int:modulo_id>/reordenar-conteudos/', views.reordenar_conteudos, name='reordenar_conteudos'),
]