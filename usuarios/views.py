from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .forms import LoginForm, CadastroForm, SalaForm
from .models import Sala
from django.contrib.auth.decorators import login_required

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
    """Exibe a página principal com as salas do usuário logado."""
    salas = Sala.objects.filter(alunos=request.user).order_by('-data_criacao')
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