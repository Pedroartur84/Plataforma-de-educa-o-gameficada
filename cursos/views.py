from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from usuarios.models import Sala
from .models import Aula, Progresso

@login_required
def lista_cursos(request):
    query = request.GET.get('q', '')
    salas = Sala.objects.filter(participantes__usuario=request.user)
    if query:
        salas = salas.filter(Q(nome__icontains=query) | Q(descricao__icontains=query))
    return render(request, 'cursos/lista_cursos.html', {'salas': salas, 'query': query})

@login_required
def detalhe_curso(request, sala_id):
    sala = get_object_or_404(Sala, id=sala_id, participantes__usuario=request.user)
    aulas = sala.aulas.order_by('ordem')

    progresso, created = Progresso.objects.get_or_create(aluno=request.user, sala=sala)
    percentual = (
        aulas.filter(concluida_por=request.user).count() / aulas.count() * 100) if aulas.count() else 0
    progresso.percentual = percentual
    progresso.save()
    return render(request, 'cursos/detalhe_curso.html', {'sala': sala, 'aulas': aulas, 'progresso': percentual})

@login_required
def marcar_aula_concluida(request, aula_id):
    # Verifica se a aula pertence a uma sala em que o usuário é participante
    aula = get_object_or_404(Aula, id=aula_id, sala__participantes__usuario=request.user)
    aula.concluida_por.add(request.user)
    return redirect('cursos:detalhe_curso', sala_id=aula.sala.id)