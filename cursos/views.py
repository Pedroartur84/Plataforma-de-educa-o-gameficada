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
    Mostra progresso e status de desbloqueio.
    """
    # Buscar salas do usuário
    participacoes = ParticipacaoSala.objects.filter(usuario=request.user).select_related('sala')
    salas_ids = participacoes.values_list('sala_id', flat=True)
    
    # Buscar trilhas dessas salas
    trilhas = Trilha.objects.filter(
        sala_id__in=salas_ids
    ).select_related('sala', 'trilha_anterior').prefetch_related(
        Prefetch('modulos', queryset=Modulo.objects.prefetch_related('conteudos'))
    ).order_by('sala__nome', 'ordem')
    
    # Calcular progresso e status de cada trilha
    trilhas_com_progresso = []
    for trilha in trilhas:
        total_conteudos = trilha.total_conteudos()
        conteudos_completos = trilha.conteudos_completos_usuario(request.user)
        progresso = trilha.progresso_usuario(request.user)
        desbloqueada = trilha.esta_desbloqueada_para(request.user)
        
        trilhas_com_progresso.append({
            'trilha': trilha,
            'progresso': progresso,
            'desbloqueada': desbloqueada,
            'total_conteudos': total_conteudos,
            'completos': conteudos_completos,
        })
    
    return render(request, 'cursos/lista_trilhas.html', {
        'trilhas_com_progresso': trilhas_com_progresso,
    })


@login_required
def detalhe_trilha(request, trilha_id):
    """
    Exibe os módulos e conteúdos de uma trilha específica.
    Mostra progresso detalhado e permite navegação.
    """
    trilha = get_object_or_404(
        Trilha.objects.select_related('sala', 'trilha_anterior'),
        id=trilha_id
    )
    
    # Verificar acesso à sala
    participacao = ParticipacaoSala.objects.filter(
        usuario=request.user,
        sala=trilha.sala
    ).first()
    
    if not participacao:
        messages.error(request, 'Você não tem acesso a esta trilha.')
        return redirect('cursos:lista_trilhas')
    
    # Verificar se está desbloqueada
    desbloqueada = trilha.esta_desbloqueada_para(request.user)
    
    if not desbloqueada:
        mensagem_bloqueio = []
        if trilha.pontos_necessarios > 0:
            faltam = trilha.pontos_necessarios - request.user.pontos_totais
            mensagem_bloqueio.append(f'Você precisa de mais {faltam} pontos')
        if trilha.trilha_anterior:
            mensagem_bloqueio.append(f'Complete a trilha "{trilha.trilha_anterior.nome}" primeiro')
        
        messages.warning(request, ' e '.join(mensagem_bloqueio) + '.')
    
    # Buscar módulos com suas informações
    modulos = trilha.modulos.prefetch_related('conteudos', 'missoes').all()
    
    modulos_com_progresso = []
    for modulo in modulos:
        conteudos_info = []
        
        for conteudo in modulo.conteudos.all():
            visualizacao = VisualizacaoConteudo.objects.filter(
                usuario=request.user,
                conteudo=conteudo
            ).first()
            
            conteudos_info.append({
                'conteudo': conteudo,
                'visualizado': visualizacao is not None,
                'completo': visualizacao.completo if visualizacao else False,
                'data_visualizacao': visualizacao.data_visualizacao if visualizacao else None,
            })
        
        # Calcular progresso do módulo
        total = len(conteudos_info)
        completos = sum(1 for c in conteudos_info if c['completo'])
        progresso = round((completos / total * 100), 1) if total > 0 else 0
        
        modulos_com_progresso.append({
            'modulo': modulo,
            'conteudos': conteudos_info,
            'progresso': progresso,
            'total': total,
            'completos': completos,
            'missoes': modulo.missoes.all(),
        })
    
    # Calcular progresso geral da trilha
    progresso_geral = trilha.progresso_usuario(request.user)
    
    context = {
        'trilha': trilha,
        'modulos_com_progresso': modulos_com_progresso,
        'desbloqueada': desbloqueada,
        'progresso_geral': progresso_geral,
        'is_professor': participacao.tipo_na_sala == 'professor',
        'participacao': participacao,
    }
    
    return render(request, 'cursos/detalhe_trilha.html', context)


@login_required
def visualizar_conteudo(request, conteudo_id):
    """
    Exibe um conteúdo específico e marca como visualizado.
    Permite marcar como completo e navegar para próximo/anterior.
    """
    conteudo = get_object_or_404(
        ConteudoModulo.objects.select_related('modulo__trilha__sala'),
        id=conteudo_id
    )
    
    trilha = conteudo.modulo.trilha
    
    # Verificar acesso
    participacao = ParticipacaoSala.objects.filter(
        usuario=request.user,
        sala=trilha.sala
    ).first()
    
    if not participacao:
        messages.error(request, 'Acesso negado.')
        return redirect('cursos:lista_trilhas')
    
    # Verificar se a trilha está desbloqueada
    if not trilha.esta_desbloqueada_para(request.user):
        messages.error(request, 'Esta trilha está bloqueada para você.')
        return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)
    
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
    Permite professor criar uma nova trilha.
    Formulário via modal no template.
    """
    sala = get_object_or_404(Sala, id=sala_id)
    
    # Verificar se é professor
    participacao = ParticipacaoSala.objects.filter(
        usuario=request.user,
        sala=sala,
        tipo_na_sala='professor'
    ).first()
    
    if not participacao:
        messages.error(request, 'Apenas professores podem criar trilhas.')
        return redirect('usuarios:sala_virtual', sala_id=sala_id)
    
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        pontos_necessarios = int(request.POST.get('pontos_necessarios', 0))
        trilha_anterior_id = request.POST.get('trilha_anterior') or None
        
        if not nome:
            messages.error(request, 'O nome da trilha é obrigatório.')
            return redirect('cursos:lista_trilhas')
        
        # Criar trilha
        ordem_atual = Trilha.objects.filter(sala=sala).count()
        
        trilha = Trilha.objects.create(
            sala=sala,
            nome=nome,
            descricao=descricao,
            pontos_necessarios=pontos_necessarios,
            trilha_anterior_id=trilha_anterior_id,
            ordem=ordem_atual,
            criador=request.user
        )
        
        messages.success(request, f'✓ Trilha "{nome}" criada com sucesso!')
        return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)
    
    return redirect('cursos:lista_trilhas')


@login_required
def criar_modulo(request, trilha_id):
    """Permite professor criar um módulo em uma trilha"""
    trilha = get_object_or_404(Trilha, id=trilha_id)
    
    # Verificar permissão
    participacao = ParticipacaoSala.objects.filter(
        usuario=request.user,
        sala=trilha.sala,
        tipo_na_sala='professor'
    ).first()
    
    if not participacao:
        messages.error(request, 'Apenas professores podem criar módulos.')
        return redirect('cursos:detalhe_trilha', trilha_id=trilha_id)
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        
        if not titulo:
            messages.error(request, 'O título do módulo é obrigatório.')
            return redirect('cursos:detalhe_trilha', trilha_id=trilha_id)
        
        ordem_atual = trilha.modulos.count()
        
        modulo = Modulo.objects.create(
            trilha=trilha,
            titulo=titulo,
            descricao=descricao,
            ordem=ordem_atual
        )
        
        messages.success(request, f'✓ Módulo "{titulo}" criado!')
        return redirect('cursos:detalhe_trilha', trilha_id=trilha_id)
    
    return redirect('cursos:detalhe_trilha', trilha_id=trilha_id)


@login_required
def adicionar_conteudo(request, modulo_id):
    """Permite professor adicionar conteúdo a um módulo"""
    modulo = get_object_or_404(Modulo, id=modulo_id)
    trilha = modulo.trilha
    
    # Verificar permissão
    participacao = ParticipacaoSala.objects.filter(
        usuario=request.user,
        sala=trilha.sala,
        tipo_na_sala='professor'
    ).first()
    
    if not participacao:
        messages.error(request, 'Apenas professores podem adicionar conteúdo.')
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
def excluir_conteudo(request, conteudo_id):
    """Permite professor excluir um conteúdo"""
    conteudo = get_object_or_404(ConteudoModulo, id=conteudo_id)
    trilha = conteudo.modulo.trilha
    
    # Verificar permissão
    participacao = ParticipacaoSala.objects.filter(
        usuario=request.user,
        sala=trilha.sala,
        tipo_na_sala='professor'
    ).first()
    
    if not participacao:
        messages.error(request, 'Apenas professores podem excluir conteúdo.')
        return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)
    
    if request.method == 'POST':
        titulo = conteudo.titulo
        conteudo.delete()
        messages.success(request, f'Conteúdo "{titulo}" excluído.')
    
    return redirect('cursos:detalhe_trilha', trilha_id=trilha.id)