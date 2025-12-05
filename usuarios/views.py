from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm, CadastroForm, SalaForm, MissaoForm, MensagemMissaoForm, CorrecaoMissaoForm
from .models import *
from django.contrib.auth.decorators import login_required
from django.db.models import Q

def login_view(request):
    """Exibe e processa o formulário de login."""
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                if not form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(0)  # Sessão do navegador
                return redirect('usuarios:pag_principal')
            else:
                messages.error(request, 'Credenciais inválidas.')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = LoginForm()
    return render(request, 'login/login.html', {'form': form})

def cadastro(request):
    """Exibe e processa o formulário de cadastro."""
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cadastro realizado com sucesso! Faça login.')
            return redirect('usuarios:pag_principal')
    else:
        form = CadastroForm()
    return render(request, 'cadastro/cadastrar.html', {'form': form})

@login_required
def principal(request):
    """Exibe a página principal com as salas do usuário logado (como aluno ou criador)."""
    salas = Sala.objects.filter(
        Q(participantes__usuario=request.user) | Q(criador=request.user)
    ).distinct().order_by('-data_criacao') # Ordenar por data de criação mais recente
    
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip().upper()
        try:
            sala = Sala.objects.get(codigo=codigo)
            if ParticipacaoSala.objects.filter(usuario=request.user, sala=sala).exists():
                messages.info(request, f'Você já está na sala {sala.nome}.')
            else:
                ParticipacaoSala.objects.create(usuario=request.user, sala=sala, tipo_na_sala='aluno')
                messages.success(request, f'Você entrou na sala {sala.nome} como aluno.')
                return redirect('usuarios:sala_virtual', sala_id=sala.id)
        except Sala.DoesNotExist:
            messages.error(request, 'Código de sala inválido.')
    return render(request, 'principal/principal_page.html', {'salas': salas})

@login_required
def criar_sala(request):
    if request.method == 'POST':
        form = SalaForm(request.POST)
        tipo_na_sala = request.POST.get('tipo_na_sala')  # rádio button no template
        
        if form.is_valid() and tipo_na_sala in ['professor', 'aluno']:
            sala = form.save(commit=False)
            sala.criador = request.user
            sala.save()

            # Criar participação do usuário na sala
            ParticipacaoSala.objects.create(
                usuario=request.user,
                sala=sala,
                tipo_na_sala=tipo_na_sala
            )
            
            messages.success(request, f"Sala '{sala.nome}' criada! Você entrou como {tipo_na_sala}.")
            return redirect('usuarios:sala_virtual', sala_id=sala.id)
        else:
            messages.error(request, 'Por favor, selecione um tipo de participação válido.')
    else:
        form = SalaForm()
    
    return render(request, 'usuarios/criar_sala.html', {
        'form': form
    })
    
@login_required
def detalhe_sala(request, sala_id):
    """Exibe os detalhes de uma sala específica."""
    sala = get_object_or_404(Sala, id=sala_id)
    # Verificar se usuário participa da sala
    participacao = ParticipacaoSala.objects.filter(usuario=request.user, sala=sala).first()
    if not participacao:
        messages.error(request, 'Você não tem acesso a esta sala.')
        return redirect('usuarios:pag_principal')
        
    return render(request, 'usuarios/detalhe_sala.html', {
        'sala': sala,
        'minha_participacao': participacao
    })

@login_required
def minhas_salas(request):
    """Exibe a lista de salas associadas ao usuário logado."""
    participacoes = ParticipacaoSala.objects.filter(usuario=request.user).select_related('sala')
    salas = [participacao.sala for participacao in participacoes]
    return render(request, 'usuarios/minhas_salas.html', {'salas': salas})

@login_required
def missoes(request):
    """Exibe a página de missões (placeholder)."""
    return render(request, 'usuarios/missoes.html')

@login_required
def ranking(request):
    """Exibe a página de ranking (placeholder)."""
    return render(request, 'usuarios/ranking.html')

@login_required
def configuracoes(request):
    """Exibe a página de configurações do usuário (placeholder)."""
    return render(request, 'usuarios/configuracoes.html')

@login_required
def painel_adm(request):
    """Exibe o painel administrativo (restrito a superusuários)."""
    if not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para acessar o Painel ADM.")
        return redirect('usuarios:pag_principal')
    return render(request, 'usuarios/painel_adm.html')

@login_required
def sala_virtual(request, sala_id):
    sala = get_object_or_404(Sala, id=sala_id)
    
    # Verificar se usuário participa da sala
    participacao = ParticipacaoSala.objects.filter(usuario=request.user, sala=sala).first()
    if not participacao:
        messages.error(request, 'Você não tem acesso a esta sala.')
        return redirect('usuarios:pag_principal')

    # MISSÕES DA SALA
    missoes_da_sala = Missao.objects.filter(sala=sala)

    # RANKING - usar participantes reais da sala
    ranking_sala = []
    participantes_alunos = ParticipacaoSala.objects.filter(sala=sala, tipo_na_sala='aluno')
    
    for participante in participantes_alunos:
        aluno = participante.usuario
        pontos_na_sala = 0
        missoes_entregues = 0

        for missao in missoes_da_sala:
            # verifiacar se o aluno foi corrigido na missão
            correcao = correcaoMissao.objects.filter(missao=missao, aluno=aluno).first()
            if correcao:
                pontos_na_sala += correcao.pontos_atingidos or 0
                missoes_entregues += 1

        ranking_sala.append({
            'aluno': aluno,
            'pontos_sala': pontos_na_sala,
            'pontos_total': aluno.pontos_totais,
            'missoes_entregues': missoes_entregues,
        })

    ranking_sala.sort(key=lambda x: x['pontos_sala'], reverse=True)
    
    for i, item in enumerate(ranking_sala, 1):
        item['posicao'] = i

    # Verificar se usuário é professor nesta sala
    is_professor_na_sala = participacao.tipo_na_sala == 'professor'

    context = {
        'sala': sala,
        'missoes': missoes_da_sala,
        'ranking_sala': ranking_sala,
        'is_professor_na_sala': is_professor_na_sala,
        'minha_participacao': participacao,
    }
    return render(request, 'usuarios/sala_virtual.html', context)

@login_required
def postar_missao(request, sala_id):
    sala = get_object_or_404(Sala, id=sala_id)
    
    # Verificar se usuário é professor nesta sala específica
    participacao = ParticipacaoSala.objects.filter(
        usuario=request.user, 
        sala=sala, 
        tipo_na_sala='professor'
    ).first()
    
    if not participacao:
        messages.error(request, 'Apenas professores desta sala podem postar missões.')
        return redirect('usuarios:sala_virtual', sala_id=sala_id)
        
    if request.method == 'POST':
        form = MissaoForm(request.POST)
        if form.is_valid():
            missao = form.save(commit=False)
            missao.sala = sala
            missao.save()
            messages.success(request, 'Missão postada com sucesso!')
            return redirect('usuarios:sala_virtual', sala_id=sala_id)
        else:
            messages.error(request, 'Erro ao postar missão. Verifique os dados.')
    
    return redirect('usuarios:sala_virtual', sala_id=sala_id)


@login_required
def chat_missao(request, missao_id):
    missao = get_object_or_404(Missao, id=missao_id)

    # Verifica se o usuário participa da sala da missão
    participacao = ParticipacaoSala.objects.filter(
        usuario=request.user,
        sala=missao.sala
    ).first()

    if not participacao:
        messages.error(request, 'Você não tem acesso a esta missão.')
        return redirect('usuarios:pag_principal')

    # Todas as mensagens do chat
    mensagens = missao.mensagens.all().order_by('data_envio')

    is_professor_na_sala = participacao.tipo_na_sala == 'professor'

    # Verifica se o aluno já entregou a missão
    ja_entregou = missao.mensagens.filter(
        usuario=request.user,
        tipo='entrega'
    ).exists()

    # === LISTA DE ENTREGAS PARA O PROFESSOR (funciona com SQLite!) ===
    entregas_com_dados = []
    if is_professor_na_sala:
        # Pega apenas os IDs dos alunos que entregaram (distinct funciona aqui no SQLite)
        alunos_com_entrega = missao.mensagens.filter(tipo='entrega')\
            .values_list('usuario_id', flat=True).distinct()

        for aluno_id in alunos_com_entrega:
            # Pega a entrega mais recente de cada aluno
            ultima_entrega = missao.mensagens.filter(
                tipo='entrega',
                usuario_id=aluno_id
            ).order_by('-data_envio').first()

            if ultima_entrega:
                entregas_com_dados.append({
                    'aluno': ultima_entrega.usuario,
                    'entrega': ultima_entrega,
                })

    # === PROCESSAMENTO DE ENVIO (POST) ===
    if request.method == 'POST' and missao.status != 'corrigida':

        # 1. Comentário normal (aluno ou professor)
        if 'texto' in request.POST and 'entregar' not in request.POST and 'corrigir' not in request.POST:
            MensagemMissao.objects.create(
                missao=missao,
                usuario=request.user,
                texto=request.POST.get('texto'),
                arquivo=request.FILES.get('arquivo'),
                tipo='comentario',
            )
            messages.success(request, 'Comentário enviado!')
            return redirect('usuarios:chat_missao', missao_id=missao_id)

        # 2. Aluno entregando a missão
        elif 'entregar' in request.POST and not ja_entregou and not is_professor_na_sala:
            MensagemMissao.objects.create(
                missao=missao,
                usuario=request.user,
                texto=request.POST.get('texto'),
                arquivo=request.FILES.get('arquivo'),
                tipo='entrega',
            )
            missao.status = 'concluida'
            missao.save()
            messages.success(request, 'Missão entregue com sucesso! Aguarde a correção.')
            return redirect('usuarios:chat_missao', missao_id=missao_id)

        # 3. Professor corrigindo um aluno
        elif 'corrigir' in request.POST and is_professor_na_sala:
            aluno_id = request.POST.get('aluno_id')
            aluno = get_object_or_404(Usuario, id=aluno_id)
            pontos_atingidos = int(request.POST.get('pontos_atingidos', 0))

            if pontos_atingidos < 0 or pontos_atingidos > missao.pontos:
                messages.error(request, f'Pontuação deve ser entre 0 e {missao.pontos}.')
            else:
                # Mensagem de correção no chat
                MensagemMissao.objects.create(
                    missao=missao,
                    usuario=request.user,
                    texto=f'Correção: {pontos_atingidos}/{missao.pontos} pontos',
                    tipo='correcao',
                )

                # Salva/atualiza a correção oficial
                correcao, created = correcaoMissao.objects.update_or_create(
                    missao=missao,
                    aluno=aluno,
                    defaults={'professor': request.user, 'pontos_atingidos': pontos_atingidos}
                )

                # Atualiza pontos totais do aluno (só soma a diferença)
                if not created and correcao.pontos_atingidos < pontos_atingidos:
                    diferenca = pontos_atingidos - correcao.pontos_atingidos
                    aluno.pontos_totais += diferenca
                    aluno.save()
                elif created:
                    aluno.pontos_totais += pontos_atingidos
                    aluno.save()

                messages.success(request, f'Correção salva! {aluno.get_nome_exibicao()} recebeu {pontos_atingidos} pontos.')

                # Verifica se todos que entregaram já foram corrigidos
                total_entregas = missao.mensagens.filter(tipo='entrega').values('usuario').distinct().count()
                total_correcoes = correcaoMissao.objects.filter(missao=missao).count()

                if total_entregas > 0 and total_entregas == total_correcoes:
                    missao.status = 'corrigida'
                    missao.save()
                    messages.info(request, 'Todas as entregas foram corrigidas. Missão finalizada!')

            return redirect('usuarios:chat_missao', missao_id=missao_id)

    # === CONTEXT PARA O TEMPLATE ===
    context = {
        'missao': missao,
        'mensagens': mensagens,
        'is_professor_na_sala': is_professor_na_sala,
        'ja_entregou': ja_entregou,
        'entregas_com_dados': entregas_com_dados,
        'minha_participacao': participacao,
    }

    return render(request, 'usuarios/chat_missao.html', context)