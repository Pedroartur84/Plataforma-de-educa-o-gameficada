from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from .forms import LoginForm, CadastroForm

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],  # O email está aqui
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                if not form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(0)  # Sessão do navegador
                return redirect('home')
            else:
                messages.error(request, 'Credenciais inválidas.')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})


def cadastro(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Cadastro realizado com sucesso! Faça login.')
            return redirect('login')
    else:
        form = CadastroForm()
    
    return render(request, 'cadastro.html', {'form': form})