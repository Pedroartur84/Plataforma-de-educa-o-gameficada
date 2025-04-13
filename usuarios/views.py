from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse

# Create your views here.
def cadastro(request):
    return render(request, 'cadastrar.html')

def login_view(request):
    if request.method == "POST":
        # Dados do formulário (email/senha são obrigatórios, remember_me é opcional)
        email = request.POST.get("email")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember_me") == "on"  # Checkbox retorna "on" se marcado

        # Autenticação padrão do Django (verifica User model)
        user = authenticate(request, username=email, password=password)
        
        if user is not None: # Se credenciais válidas
            login(request, user) # Cria a sessão do usuário
            
            # Configura expiração da sessão:
            # - 30 dias se "Lembrar-me" ativado
            # - Sessão de navegador se desativado
            if remember_me:
                request.session.set_expiry(30 * 24 * 60 * 60)  # Cookie expira em 30 dias
            else:
                request.session.set_expiry(0)  # Cookie expira quando o navegador fecha
            return redirect("home") # Redireciona para URL nomeada 'home'
        else:
            # Credenciais inválidas - mantém na página com erro
            return render(request, "login.html", {"error": "E-mail ou senha inválidos."})
    
    return render(request, "login.html")