from django.urls import path
from . import views

app_name = 'cursos' #para que os nomes das rotas agrupadas sejam reconhecidas e posam ser usadas

urlpatterns = [
    path('', views.lista_cursos, name='lista_cursos'),
    path('sala/<int:sala_id>/', views.detalhe_curso, name='detalhe_curso'),  # Ajuste para 'sala'
    path('aula/<int:aula_id>/concluir/', views.marcar_aula_concluida, name='marcar_aula_concluida'),
]