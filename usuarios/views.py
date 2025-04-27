from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from .forms import LoginForm, CadastroForm

def login_view(request):
    # verifica se a requisição é do tipo POST
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        # verifica se o formulario é válido
        if form.is_valid():
            # tenta autenticar o usuario com as credencias fornecidas
            user = authenticate(
                username=form.cleaned_data['username'],  # O email está aqui
                password=form.cleaned_data['password']
            )
            # se o usuario foi autenticado com sucesso
            if user is not None:
                # faz o login do usuario
                login(request, user)
                # verifica se o usuário marcou "lembrarme"
                if not form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(0)  # Sessão do navegador
                return redirect('home')
            else:
                messages.error(request, 'Credenciais inválidas.')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = LoginForm()
    
    return render(request, 'login\login.html', {'form': form})

# view para cadastro
def cadastro(request):
    # verifica se a requisicao e do tipo POST
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        # verifica se o formulario e valido
        if form.is_valid():
            # salva o novo usuario no banco de dados
            user = form.save()
            login(request, user)
            messages.success(request, 'Cadastro realizado com sucesso! Faça login.')
            return redirect('home')
    else:
        form = CadastroForm()
    
    return render(request, 'cadastro\cadastrar.html', {'form': form})