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
            if (missao.status == 'corrigida' and 
                missao.mensagens.filter(usuario=aluno).exists()):
                pontos_na_sala += missao.pontos_atingidos or 0
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
    
    # Verificar se usuário tem acesso à missão (participa da sala)
    participacao = ParticipacaoSala.objects.filter(
        usuario=request.user, 
        sala=missao.sala
    ).first()
    
    if not participacao:
        messages.error(request, 'Você não tem acesso a esta missão.')
        return redirect('usuarios:pag_principal')
        
    mensagens = missao.mensagens.all().order_by('data_envio')
    is_professor_na_sala = participacao.tipo_na_sala == 'professor'

    if request.method == 'POST':
        if missao.status == 'corrigida':
            messages.error(request, 'Esta missão já foi corrigida.')
        else:
            # Envio de mensagem normal (aluno)
            if 'texto' in request.POST:
                texto = request.POST.get('texto')
                arquivo = request.FILES.get('arquivo')
                MensagemMissao.objects.create(
                    missao=missao,
                    usuario=request.user,
                    texto=texto,
                    arquivo=arquivo
                )
                # Se for a primeira mensagem → missão concluída
                if mensagens.count() == 0:
                    missao.status = 'concluida'
                    missao.save()
                return redirect('usuarios:chat_missao', missao_id=missao_id)

            # Correção pelo professor
            elif 'corrigir_missao' in request.POST and is_professor_na_sala:
                pontos_atingidos = int(request.POST.get('pontos_atingidos', 0))
                if pontos_atingidos > missao.pontos:
                    messages.error(request, f'Pontos não podem exceder {missao.pontos}')
                else:
                    missao.pontos_atingidos = pontos_atingidos
                    missao.status = 'corrigida'
                    missao.save()

                    # SOMAR PONTOS AO ALUNO
                    primeira_mensagem = mensagens.first()
                    if primeira_mensagem and primeira_mensagem.usuario != request.user:
                        aluno = primeira_mensagem.usuario
                        aluno.pontos_totais += pontos_atingidos
                        aluno.save()

                        messages.success(request,
                            f'Correção salva! {aluno.get_nome_exibicao()} ganhou {pontos_atingidos} pontos. '
                            f'Total dele: {aluno.pontos_totais} pts')
                    else:
                        messages.success(request, f'Missão corrigida com {pontos_atingidos} pontos.')

                return redirect('usuarios:chat_missao', missao_id=missao_id)

    context = {
        'missao': missao,
        'mensagens': mensagens,
        'is_professor_na_sala': is_professor_na_sala,
        'minha_participacao': participacao,
    }
    return render(request, 'usuarios/chat_missao.html', context)