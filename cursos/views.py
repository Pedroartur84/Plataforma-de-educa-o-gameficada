# cursos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Prefetch
from django.http import JsonResponse
from usuarios.models import Sala, ParticipacaoSala, Missao
from .models import (
    Trilha, Modulo, ConteudoModulo, VisualizacaoConteudo,
    Aula, Progresso  # Mantidos para compatibilidade
)

# ==============================
# VIEWS ANTIGAS (manter para compatibilidade)
# ==============================
@login_required
def lista_cursos(request):
    """DEPRECATED - Redireciona para lista de trilhas"""
    return redirect('cursos:lista_trilhas')


@login_required
def detalhe_curso(request, sala_id):
    """DEPRECATED - Mantido apenas para links antigos"""
    sala = get_object_or_404(Sala, id=sala_id, participantes__usuario=request.user)
    aulas = sala.aulas.order_by('ordem')
    
    progresso, created = Progresso.objects.get_or_create(aluno=request.user, sala=sala)
    percentual = (
        aulas.filter(concluida_por=request.user).count() / aulas.count() * 100
    ) if aulas.count() else 0
    progresso.percentual = percentual
    progresso.save()
    
    return render(request, 'cursos/detalhe_curso.html', {
        'sala': sala,
        'aulas': aulas,
        'progresso': percentual
    })


@login_required
def marcar_aula_concluida(request, aula_id):
    """DEPRECATED - Mantido para compatibilidade"""
    aula = get_object_or_404(Aula, id=aula_id, sala__participantes__usuario=request.user)
    aula.concluida_por.add(request.user)
    return redirect('cursos:detalhe_curso', sala_id=aula.sala.id)


# ==============================
# VIEWS DO NOVO SISTEMA DE TRILHAS
# ==============================
@login_required
def lista_trilhas(request):
    """
    Lista todas as trilhas disponíveis nas salas do usuário.
    Mostra progresso visual (% de conteúdos completados).
    """
    # Buscar salas do usuário
    participacoes = ParticipacaoSala.objects.filter(usuario=request.user).select_related('sala')
    salas_ids = participacoes.values_list('sala_id', flat=True)
    
    # Buscar trilhas dessas salas
    trilhas = Trilha.objects.filter(
        sala_id__in=salas_ids
    ).select_related('sala', 'professor').prefetch_related(
        Prefetch('modulos', queryset=Modulo.objects.prefetch_related('conteudos'))
    ).order_by('sala__nome', 'ordem')
    
    # Calcular progresso de cada trilha
    trilhas_com_progresso = []
    for trilha in trilhas:
        total_conteudos = trilha.total_conteudos()
        conteudos_completos = trilha.conteudos_completos_usuario(request.user)
        conteudos_visualizados = trilha.conteudos_visualizados_usuario(request.user)
        progresso = trilha.progresso_usuario(request.user)
        
        # Verificar se o usuário é o professor desta trilha
        eh_professor = (
            trilha.professor == request.user or 
            request.user.tipo_usuario == 'admin'
        )
        
        trilhas_com_progresso.append({
            'trilha': trilha,
            'progresso': progresso,
            'total_conteudos': total_conteudos,
            'completos': conteudos_completos,
            'visualizados': conteudos_visualizados,
            'eh_professor': eh_professor,
        })
    
    return render(request, 'cursos/lista_trilhas.html', {
        'trilhas_com_progresso': trilhas_com_progresso,
    })


@login_required
def detalhe_trilha(request, trilha_id):
    """
    Retorna informações da trilha em JSON (para modais).
    Mostra informações básicas: nome, descrição, progresso.
    
    Permissões:
    - Qualquer participante da sala pode acessar
    """
    trilha = get_object_or_404(
        Trilha.objects.select_related('sala', 'professor'),
        id=trilha_id
    )
    
    # Verificar acesso à sala
    participacao = ParticipacaoSala.objects.filter(
        usuario=request.user,
        sala=trilha.sala
    ).first()
    
    if not participacao:
        return JsonResponse({'error': 'Sem acesso'}, status=403)
    
    # Calcular progresso geral da trilha
    progresso_geral = trilha.progresso_usuario(request.user)
    
    data = {
        'id': trilha.id,
        'nome': trilha.nome,
        'descricao': trilha.descricao,
        'progresso': progresso_geral,
        'professor': trilha.professor.get_nome_exibicao(),
        'pontos_necessarios': trilha.pontos_necessarios,
    }
    
    return JsonResponse(data)


@login_required
def visualizar_conteudo(request, conteudo_id):
    """
    Exibe um conteúdo específico e marca como visualizado.
    Permite marcar como completo e navegar para próximo/anterior.
    
    NÃO HÁ BLOQUEIOS: qualquer aluno pode visualizar qualquer conteúdo.
    """
    conteudo = get_object_or_404(
        ConteudoModulo.objects.select_related('modulo__trilha__sala'),
        id=conteudo_id
    )
    
    trilha = conteudo.modulo.trilha
    
    # Verificar acesso à sala
    participacao = ParticipacaoSala.objects.filter(
        usuario=request.user,
        sala=trilha.sala
    ).first()
    
    if not participacao:
        messages.error(request, 'Acesso negado.')
        return redirect('cursos:lista_trilhas')
    
    # Criar ou buscar visualização
    visualizacao, created = VisualizacaoConteudo.objects.get_or_create(
        usuario=request.user,
        conteudo=conteudo
    )
    
    # Processar POST (marcar como completo/incompleto)
    if request.method == 'POST':
        if 'marcar_completo' in request.POST:
            visualizacao.completo = True
            visualizacao.save()
            messages.success(request, '✓ Conteúdo marcado como completo!')
            
            # Redirecionar para próximo conteúdo
            proximo = conteudo.proximo_conteudo()
            if proximo:
                return redirect('cursos:visualizar_conteudo', conteudo_id=proximo.id)
            else:
                # Verificar se tem próximo módulo
                proximo_modulo = Modulo.objects.filter(
                    trilha=trilha,
                    ordem__gt=conteudo.modulo.ordem
                ).first()
                
                if proximo_modulo and proximo_modulo.conteudos.exists():
                    primeiro_conteudo = proximo_modulo.conteudos.first()
                    messages.info(request, f'Próximo módulo: {proximo_modulo.titulo}')
                    return redirect('cursos:visualizar_conteudo', conteudo_id=primeiro_conteudo.id)
                else:
                    messages.success(request, '🎉 Parabéns! Você completou toda a trilha!')
                    return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)
        
        elif 'marcar_incompleto' in request.POST:
            visualizacao.completo = False
            visualizacao.save()
            messages.info(request, 'Conteúdo marcado como incompleto.')
    
    # Buscar todos os conteúdos do módulo para navegação
    conteudos_modulo = conteudo.modulo.conteudos.all()
    
    # Identificar posição atual
    posicao_atual = list(conteudos_modulo).index(conteudo) + 1
    total_conteudos = conteudos_modulo.count()
    
    # Conteúdo anterior e próximo
    anterior = conteudo.conteudo_anterior()
    proximo = conteudo.proximo_conteudo()
    
    context = {
        'conteudo': conteudo,
        'trilha': trilha,
        'modulo': conteudo.modulo,
        'visualizacao': visualizacao,
        'conteudos_modulo': conteudos_modulo,
        'posicao_atual': posicao_atual,
        'total_conteudos': total_conteudos,
        'anterior': anterior,
        'proximo': proximo,
    }
    
    return render(request, 'cursos/visualizar_conteudo.html', context)


@login_required
def criar_trilha(request, sala_id):
    """
    Permite PROFESSOR criar uma nova trilha nessa sala.
    
    Permissões: SOMENTE professor dessa sala pode criar
    """
    sala = get_object_or_404(Sala, id=sala_id)
    
    # Verificar se é professor dessa sala
    participacao = ParticipacaoSala.objects.filter(
        usuario=request.user,
        sala=sala,
        tipo_na_sala='professor'
    ).first()
    
    if not participacao:
        messages.error(request, 'Apenas professores podem criar trilhas nesta sala.')
        return redirect('usuarios:sala_virtual', sala_id=sala_id)
    
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        
        if not nome:
            messages.error(request, 'O nome da trilha é obrigatório.')
            return redirect('usuarios:sala_virtual', sala_id=sala_id)
        
        # Verificar se já existe trilha com esse nome nessa sala
        if Trilha.objects.filter(sala=sala, nome=nome).exists():
            messages.error(request, 'Já existe uma trilha com este nome nesta sala.')
            return redirect('usuarios:sala_virtual', sala_id=sala_id)
        
        # Criar trilha
        ordem_atual = Trilha.objects.filter(sala=sala).count()
        
        trilha = Trilha.objects.create(
            sala=sala,
            nome=nome,
            descricao=descricao,
            ordem=ordem_atual,
            professor=request.user  # O professor responsável é quem criou
        )
        
        messages.success(request, f'✓ Trilha "{nome}" criada com sucesso!')
        return redirect('usuarios:sala_virtual', sala_id=sala_id)
    
    return redirect('usuarios:sala_virtual', sala_id=sala_id)


@login_required
def editar_trilha(request, trilha_id):
    """
    Permite PROFESSOR editar uma trilha.
    
    Permissões: SOMENTE professor responsável pela trilha
    """
    trilha = get_object_or_404(Trilha, id=trilha_id)
    
    # Verificar permissão: é o professor da trilha?
    if trilha.professor != request.user and request.user.tipo_usuario != 'admin':
        messages.error(request, 'Você não tem permissão para editar esta trilha.')
        return redirect('usuarios:sala_virtual', sala_id=trilha.sala.id)
    
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        
        if not nome:
            messages.error(request, 'O nome da trilha é obrigatório.')
            return redirect('usuarios:sala_virtual', sala_id=trilha.sala.id)
        
        # Verificar se outro já tem esse nome (exceto ele mesmo)
        if Trilha.objects.filter(sala=trilha.sala, nome=nome).exclude(id=trilha.id).exists():
            messages.error(request, 'Já existe outra trilha com este nome nesta sala.')
            return redirect('usuarios:sala_virtual', sala_id=trilha.sala.id)
        
        trilha.nome = nome
        trilha.descricao = descricao
        trilha.save()
        
        messages.success(request, f'✓ Trilha "{nome}" atualizada com sucesso!')
        return redirect('usuarios:sala_virtual', sala_id=trilha.sala.id)
    
    return redirect('usuarios:sala_virtual', sala_id=trilha.sala.id)


@login_required
def excluir_trilha(request, trilha_id):
    """
    Permite PROFESSOR excluir uma trilha (e todos seus módulos/conteúdos).
    
    Permissões: SOMENTE professor responsável pela trilha
    """
    trilha = get_object_or_404(Trilha, id=trilha_id)
    sala_id = trilha.sala.id
    
    # Verificar permissão
    if trilha.professor != request.user and request.user.tipo_usuario != 'admin':
        messages.error(request, 'Você não tem permissão para excluir esta trilha.')
        return redirect('usuarios:sala_virtual', sala_id=sala_id)
    
    if request.method == 'POST':
        nome_trilha = trilha.nome
        trilha.delete()
        messages.success(request, f'✓ Trilha "{nome_trilha}" excluída com sucesso!')
        return redirect('usuarios:sala_virtual', sala_id=sala_id)
    
    # GET: retornar erro (modais não devem fazer GET para excluir)
    messages.error(request, 'Método não permitido. Use o formulário de exclusão.')
    return redirect('usuarios:sala_virtual', sala_id=sala_id)


@login_required
def reordenar_trilhas(request, sala_id):
    """
    Permite PROFESSOR reordenar as trilhas da sala.
    
    Recebe JSON com nova ordem via AJAX.
    """
    sala = get_object_or_404(Sala, id=sala_id)
    
    # Verificar se é professor dessa sala
    participacao = ParticipacaoSala.objects.filter(
        usuario=request.user,
        sala=sala,
        tipo_na_sala='professor'
    ).first()
    
    if not participacao and request.user.tipo_usuario != 'admin':
        return JsonResponse({'erro': 'Sem permissão'}, status=403)
    
    if request.method == 'POST':
        try:
            import json
            dados = json.loads(request.body)
            nova_ordem = dados.get('ordem', [])
            
            # Atualizar ordem das trilhas
            for idx, trilha_id in enumerate(nova_ordem):
                Trilha.objects.filter(id=trilha_id, sala=sala).update(ordem=idx)
            
            return JsonResponse({'sucesso': True})
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=400)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)


@login_required
def criar_modulo(request, trilha_id):
    """
    Permite PROFESSOR criar um módulo em uma trilha.
    
    Permissões: SOMENTE professor responsável pela trilha
    """
    trilha = get_object_or_404(Trilha, id=trilha_id)
    
    # Verificar permissão
    if trilha.professor != request.user and request.user.tipo_usuario != 'admin':
        messages.error(request, 'Apenas o professor desta trilha pode criar módulos.')
        return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        
        if not titulo:
            messages.error(request, 'O título do módulo é obrigatório.')
            return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)
        
        ordem_atual = trilha.modulos.count()
        
        modulo = Modulo.objects.create(
            trilha=trilha,
            titulo=titulo,
            descricao=descricao,
            ordem=ordem_atual
        )
        
        messages.success(request, f'✓ Módulo "{titulo}" criado!')
        return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)
    
    return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)


@login_required
def editar_modulo(request, modulo_id):
    """
    Permite PROFESSOR editar um módulo.
    """
    modulo = get_object_or_404(Modulo, id=modulo_id)
    trilha = modulo.trilha
    
    # Verificar permissão
    if trilha.professor != request.user and request.user.tipo_usuario != 'admin':
        messages.error(request, 'Sem permissão para editar este módulo.')
        return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        
        if not titulo:
            messages.error(request, 'O título do módulo é obrigatório.')
            return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)
        
        modulo.titulo = titulo
        modulo.descricao = descricao
        modulo.save()
        
        messages.success(request, f'✓ Módulo "{titulo}" atualizado!')
        return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)
    
    return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)


@login_required
def excluir_modulo(request, modulo_id):
    """
    Permite PROFESSOR excluir um módulo (e seus conteúdos).
    """
    modulo = get_object_or_404(Modulo, id=modulo_id)
    trilha = modulo.trilha
    
    # Verificar permissão
    if trilha.professor != request.user and request.user.tipo_usuario != 'admin':
        messages.error(request, 'Sem permissão para excluir este módulo.')
        return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)
    
    if request.method == 'POST':
        titulo = modulo.titulo
        modulo.delete()
        messages.success(request, f'✓ Módulo "{titulo}" excluído!')
        return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)
    
    return render(request, 'cursos/confirmar_excluir_modulo.html', {
        'modulo': modulo,
        'trilha': trilha,
    })


@login_required
def reordenar_modulos(request, trilha_id):
    """
    Permite PROFESSOR reordenar módulos da trilha via AJAX.
    """
    trilha = get_object_or_404(Trilha, id=trilha_id)
    
    # Verificar permissão
    if trilha.professor != request.user and request.user.tipo_usuario != 'admin':
        return JsonResponse({'erro': 'Sem permissão'}, status=403)
    
    if request.method == 'POST':
        try:
            import json
            dados = json.loads(request.body)
            nova_ordem = dados.get('ordem', [])
            
            # Atualizar ordem dos módulos
            for idx, modulo_id in enumerate(nova_ordem):
                Modulo.objects.filter(id=modulo_id, trilha=trilha).update(ordem=idx)
            
            return JsonResponse({'sucesso': True})
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=400)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)


@login_required
def adicionar_conteudo(request, modulo_id):
    """
    Permite PROFESSOR adicionar conteúdo a um módulo.
    
    Permissões: SOMENTE professor responsável pela trilha
    """
    modulo = get_object_or_404(Modulo, id=modulo_id)
    trilha = modulo.trilha
    
    # Verificar permissão
    if trilha.professor != request.user and request.user.tipo_usuario != 'admin':
        messages.error(request, 'Apenas o professor desta trilha pode adicionar conteúdo.')
        return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        tipo = request.POST.get('tipo')
        conteudo_texto = request.POST.get('conteudo', '').strip()
        link = request.POST.get('link', '').strip()
        arquivo = request.FILES.get('arquivo')
        duracao = int(request.POST.get('duracao_estimada', 0))
        
        if not titulo or not tipo:
            messages.error(request, 'Título e tipo são obrigatórios.')
            return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)
        
        ordem_atual = modulo.conteudos.count()
        
        conteudo = ConteudoModulo.objects.create(
            modulo=modulo,
            titulo=titulo,
            tipo=tipo,
            conteudo=conteudo_texto,
            link=link,
            arquivo=arquivo,
            duracao_estimada=duracao,
            ordem=ordem_atual
        )
        
        messages.success(request, f'✓ Conteúdo "{titulo}" adicionado!')
        return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)
    
    return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)


@login_required
def editar_conteudo(request, conteudo_id):
    """
    Permite PROFESSOR editar um conteúdo.
    """
    conteudo = get_object_or_404(ConteudoModulo, id=conteudo_id)
    trilha = conteudo.modulo.trilha
    
    # Verificar permissão
    if trilha.professor != request.user and request.user.tipo_usuario != 'admin':
        messages.error(request, 'Sem permissão para editar este conteúdo.')
        return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        tipo = request.POST.get('tipo')
        conteudo_texto = request.POST.get('conteudo', '').strip()
        link = request.POST.get('link', '').strip()
        arquivo = request.FILES.get('arquivo')
        duracao = int(request.POST.get('duracao_estimada', 0))
        
        if not titulo or not tipo:
            messages.error(request, 'Título e tipo são obrigatórios.')
            return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)
        
        conteudo.titulo = titulo
        conteudo.tipo = tipo
        conteudo.conteudo = conteudo_texto
        conteudo.link = link
        conteudo.duracao_estimada = duracao
        
        if arquivo:
            conteudo.arquivo = arquivo
        
        conteudo.save()
        
        messages.success(request, f'✓ Conteúdo "{titulo}" atualizado!')
        return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)
    
    return render(request, 'cursos/editar_conteudo.html', {
        'conteudo': conteudo,
        'trilha': trilha,
    })


@login_required
def excluir_conteudo(request, conteudo_id):
    """
    Permite PROFESSOR excluir um conteúdo.
    """
    conteudo = get_object_or_404(ConteudoModulo, id=conteudo_id)
    trilha = conteudo.modulo.trilha
    
    # Verificar permissão
    if trilha.professor != request.user and request.user.tipo_usuario != 'admin':
        messages.error(request, 'Sem permissão para excluir este conteúdo.')
        return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)
    
    if request.method == 'POST':
        titulo = conteudo.titulo
        conteudo.delete()
        messages.success(request, f'✓ Conteúdo "{titulo}" excluído.')
        return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)
    
    return render(request, 'cursos/confirmar_excluir_conteudo.html', {
        'conteudo': conteudo,
        'trilha': trilha,
    })


@login_required
def reordenar_conteudos(request, modulo_id):
    """
    Permite PROFESSOR reordenar conteúdos do módulo via AJAX.
    """
    modulo = get_object_or_404(Modulo, id=modulo_id)
    trilha = modulo.trilha
    
    # Verificar permissão
    if trilha.professor != request.user and request.user.tipo_usuario != 'admin':
        return JsonResponse({'erro': 'Sem permissão'}, status=403)
    
    if request.method == 'POST':
        try:
            import json
            dados = json.loads(request.body)
            nova_ordem = dados.get('ordem', [])
            
            # Atualizar ordem dos conteúdos
            for idx, conteudo_id in enumerate(nova_ordem):
                ConteudoModulo.objects.filter(id=conteudo_id, modulo=modulo).update(ordem=idx)
            
            return JsonResponse({'sucesso': True})
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=400)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)