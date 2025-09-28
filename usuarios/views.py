from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm, CadastroForm, SalaForm, MensagemForm, MissaoForm, MensagemMissaoForm
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
    salas = Sala.objects.filter(Q(alunos=request.user) | Q(criador=request.user)).order_by('-data_criacao')
    return render(request, 'principal/principal_page.html', {'salas': salas})

@login_required
def criar_sala(request):
    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            sala = form.save(commit=False)
            sala.criador = request.user
            sala.save()
            if sala.tipo_usuario_criador == 'aluno':
                sala.alunos.add(request.user)
            # se for professor, o criador já está associado via criador, sem necessidade de adicionar a alunos
            messages.success(request, 'Sala criada')
            return redirect('usuarios:pag_principal')
        else:
            messages.error(request, 'Corrija os erros do formulario.')
    else:
        form = SalaForm()
        return render(request, 'usuarios/criar_sala.html', {'form': form})
    
@login_required
def detalhe_sala(request, sala_id):
    """Exibe os detalhes de uma sala específica."""
    sala = get_object_or_404(Sala, id=sala_id, alunos=request.user)
    return render(request, 'usuarios/detalhe_sala.html', {'sala': sala})

@login_required
def minhas_salas(request):
    """Exibe a lista de salas associadas ao usuário logado."""
    salas = Sala.objects.filter(alunos=request.user).order_by('-data_criacao')
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
    sala.alunos.add(request.user)
    mensagens = Mensagem.objects.filter(sala=sala).order_by('data_envio')
    missões = Missao.objects.filter(sala=sala).order_by('-data_criacao')
    form = MensagemForm()
    missao_form = MissaoForm()  # Adicionado para o modal
    if request.method == 'POST':
        mensagem_form = MensagemForm(request.POST)
        if mensagem_form.is_valid():
            mensagem = mensagem_form.save(commit=False)
            mensagem.sala = sala
            mensagem.usuario = request.user
            mensagem.save()
            messages.success(request, 'Mensagem enviada!')
            return redirect('usuarios:sala_virtual', sala_id=sala_id)
    else:
        mensagem_form = MensagemForm()
    return render(request, 'usuarios/sala_virtual.html', {
        'sala': sala,
        'mensagens': mensagens,
        'missões': missões,
        'form': mensagem_form,
        'form_missao': missao_form  # Passado ao template
    })

@login_required
def postar_missao(request, sala_id):
    sala = get_object_or_404(Sala, id=sala_id)
    if sala.tipo_usuario_criador != 'professor' or request.user != sala.criador:
        messages.error(request, 'Apenas professores podem postar missões.')
        return redirect('usuarios:sala_virtual', sala_id=sala_id)
    if request.method == 'POST':
        form = MissaoForm(request.POST)
        if form.is_valid():
            missao = form.save(commit=False)
            missao.sala = sala
            missao.professor = request.user
            missao.save()
            messages.success(request, 'Missão postada com sucesso!')
            return redirect('usuarios:sala_virtual', sala_id=sala_id)
    else:
        form = MissaoForm()
    return render(request, 'usuarios/postar_missao.html', {'form': form, 'sala': sala})

@login_required
def chat_missao(request, missao_id):
    missao = get_object_or_404(Missao, id=missao_id)
    mensagens = MensagemMissao.objects.filter(missao=missao).order_by('data_envio')
    form = MensagemMissaoForm()
    return render(request, 'usuarios/chat_missao.html', {'missao': missao, 'mensagens': mensagens, 'form': form})