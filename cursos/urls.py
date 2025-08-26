from django.urls import path
from . import views

app_name = 'cursos' #para que os nomes das rotas agrupadas sejam reconhecidas e posam ser usadas

urlpatterns = [
    path('', views.lista_cursos, name='lista_cursos'), #página que lista os cursos disponíveis
    path('curso/<int:sala_id>/', views.detalhe_curso, name='detalhe_curso'), #página de detalhes do curso
    path('aula/<int:aula_id>/concluir/', views.marcar_aula_concluida, name='marcar_aula_concluida'), #marcar aula como concluída
]