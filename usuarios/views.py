from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm, CadastroForm, SalaForm, MissaoForm, MensagemMissaoForm, CorrecaoMissaoForm, PerfilForm
from .models import *
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Sum
from django.http import JsonResponse, HttpResponseBadRequest
import json

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
    
    # Buscar todos os títulos globais
    titulos_globais = Titulo.objects.filter(tipo='global').order_by('pontos_necessarios')
    
    context = {
        'titulos_globais': titulos_globais,
    }
    
    return render(request, 'usuarios/painel_adm.html', context)

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

    # TÍTULOS DA SALA
    titulos_sala = Titulo.objects.filter(tipo='sala')

    # Verificar se usuário é professor nesta sala
    is_professor_na_sala = participacao.tipo_na_sala == 'professor'

    context = {
        'sala': sala,
        'missoes': missoes_da_sala,
        'ranking_sala': ranking_sala,
        'is_professor_na_sala': is_professor_na_sala,
        'minha_participacao': participacao,
        'titulos_sala': titulos_sala,
    }
    return render(request, 'usuarios/sala_virtual.html', context)


@login_required
def sala_messages(request, sala_id):
    """API simples para obter e postar mensagens do chat geral da sala.

    GET: retorna JSON com as últimas mensagens (até 100)
    POST: cria uma nova mensagem (espera campo 'texto' em form-data ou JSON)
    """
    sala = get_object_or_404(Sala, id=sala_id)

    # Verificar se usuário participa da sala
    participacao = ParticipacaoSala.objects.filter(usuario=request.user, sala=sala).first()
    if not participacao:
        return JsonResponse({'error': 'Acesso negado à sala.'}, status=403)

    if request.method == 'GET':
        msgs = ChatMessage.objects.filter(sala=sala).order_by('-criado_em')[:100]
        msgs = reversed(list(msgs))
        data = [
            {
                'id': m.id,
                'usuario_id': m.usuario.id,
                'usuario_nome': m.usuario.get_nome_exibicao(),
                'texto': m.texto,
                'criado_em': m.criado_em.isoformat(),
            }
            for m in msgs
        ]
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        # suporta form-data ou JSON
        texto = request.POST.get('texto')
        if not texto:
            try:
                body = json.loads(request.body.decode('utf-8') or '{}')
                texto = body.get('texto')
            except Exception:
                texto = None

        if not texto or not texto.strip():
            return HttpResponseBadRequest('Campo texto é obrigatório.')

        msg = ChatMessage.objects.create(sala=sala, usuario=request.user, texto=texto.strip())

        data = {
            'id': msg.id,
            'usuario_id': msg.usuario.id,
            'usuario_nome': msg.usuario.get_nome_exibicao(),
            'texto': msg.texto,
            'criado_em': msg.criado_em.isoformat(),
        }
        return JsonResponse(data, status=201)

    else:
        return JsonResponse({'error': 'Método não permitido.'}, status=405)

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

        # 4. Professor anexando arquivo à missão
        elif 'anexar_arquivo' in request.POST and is_professor_na_sala:
            arquivo = request.FILES.get('anexo_arquivo')
            nome = request.POST.get('anexo_nome', '').strip()
            
            if arquivo:
                AnexoMissao.objects.create(
                    missao=missao,
                    arquivo=arquivo,
                    nome=nome if nome else None
                )
                messages.success(request, 'Arquivo anexado com sucesso!')
            else:
                messages.error(request, 'Selecione um arquivo para anexar.')
            
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


@login_required
def missao_messages(request, missao_id):
    """API simples para obter mensagens do chat da missão.

    GET: retorna JSON com as últimas mensagens (até 100)
    """
    missao = get_object_or_404(Missao, id=missao_id)

    # Verificar se usuário participa da sala da missão
    participacao = ParticipacaoSala.objects.filter(usuario=request.user, sala=missao.sala).first()
    if not participacao:
        return JsonResponse({'error': 'Acesso negado à missão.'}, status=403)

    if request.method == 'GET':
        msgs = MensagemMissao.objects.filter(missao=missao).order_by('-data_envio')[:100]
        msgs = reversed(list(msgs))
        data = [
            {
                'id': m.id,
                'usuario_id': m.usuario.id,
                'usuario_nome': m.usuario.get_nome_exibicao(),
                'texto': m.texto,
                'arquivo': m.arquivo.url if m.arquivo else None,
                'tipo': m.tipo,
                'data_envio': m.data_envio.isoformat(),
            }
            for m in msgs
        ]
        return JsonResponse(data, safe=False)

    else:
        return JsonResponse({'error': 'Método não permitido.'}, status=405)



@login_required
def perfil(request):
    """View unificada para exibir e editar perfil."""
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('usuarios:perfil')
        else:
            messages.error(request, 'Erro ao atualizar perfil. Verifique os dados.')
    else:
        form = PerfilForm(instance=request.user)
    
    # Verificar e conceder títulos globais automaticamente
    request.user.verificar_titulos_globais()
    
    context = {
        'form': form,
        'usuario': request.user,
        'titulos_globais': request.user.titulos_globais.all(),
    }
    return render(request, 'usuarios/perfil.html', context)


@login_required
def listar_titulos(request):
    """
    Lista todos os títulos disponíveis (globais e de salas).
    Mostra quais o usuário já conquistou e o progresso dos restantes.
    """
    # TÍTULOS GLOBAIS
    titulos_globais = Titulo.objects.filter(tipo='global').order_by('pontos_necessarios')
    
    titulos_globais_info = []
    for titulo in titulos_globais:
        conquistado = titulo in request.user.titulos_globais.all()
        
        # Calcular progresso
        progresso_pontos = 0
        progresso_missoes = 0
        
        if not conquistado:
            if titulo.pontos_necessarios > 0:
                progresso_pontos = min(100, int((request.user.pontos_totais / titulo.pontos_necessarios) * 100))
            
            missoes_completadas = request.user.missoes_completadas_globais()
            if titulo.missoes_necessarias > 0:
                progresso_missoes = min(100, int((missoes_completadas / titulo.missoes_necessarias) * 100))
        
        titulos_globais_info.append({
            'titulo': titulo,
            'conquistado': conquistado,
            'progresso_pontos': progresso_pontos,
            'progresso_missoes': progresso_missoes,
            'missoes_completadas': request.user.missoes_completadas_globais(),
        })
    
    # TÍTULOS DE SALAS
    participacoes = ParticipacaoSala.objects.filter(usuario=request.user).select_related('sala')
    
    titulos_salas_info = []
    for participacao in participacoes:
        titulos_sala = Titulo.objects.filter(tipo='sala')
        
        for titulo in titulos_sala:
            conquistado = titulo in participacao.titulos_sala.all()
            pontos_na_sala = participacao.calcular_pontos_na_sala()
            missoes_na_sala = participacao.missoes_completadas_na_sala()
            
            progresso_pontos = 0
            progresso_missoes = 0
            
            if not conquistado:
                if titulo.pontos_necessarios > 0:
                    progresso_pontos = min(100, int((pontos_na_sala / titulo.pontos_necessarios) * 100))
                if titulo.missoes_necessarias > 0:
                    progresso_missoes = min(100, int((missoes_na_sala / titulo.missoes_necessarias) * 100))
            
            titulos_salas_info.append({
                'titulo': titulo,
                'sala': participacao.sala,
                'conquistado': conquistado,
                'progresso_pontos': progresso_pontos,
                'progresso_missoes': progresso_missoes,
                'pontos_na_sala': pontos_na_sala,
                'missoes_na_sala': missoes_na_sala,
            })
    
    context = {
        'titulos_globais_info': titulos_globais_info,
        'titulos_salas_info': titulos_salas_info,
    }
    
    return render(request, 'usuarios/titulos.html', context)


@login_required
def criar_titulo_sala(request, sala_id):
    """
    Permite que professores criem títulos específicos para suas salas.
    Apenas professores da sala podem criar títulos.
    """
    sala = get_object_or_404(Sala, id=sala_id)
    
    # Verificar se usuário é professor nesta sala
    participacao = ParticipacaoSala.objects.filter(
        usuario=request.user, 
        sala=sala, 
        tipo_na_sala='professor'
    ).first()
    
    if not participacao:
        messages.error(request, 'Apenas professores desta sala podem criar títulos.')
        return redirect('usuarios:sala_virtual', sala_id=sala_id)
    
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        pontos_necessarios = request.POST.get('pontos_necessarios', 0)
        missoes_necessarias = request.POST.get('missoes_necessarias', 0)
        icone = request.FILES.get('icone')
        
        # Validações
        if not nome or not descricao:
            messages.error(request, 'Nome e descrição são obrigatórios.')
            return redirect('usuarios:sala_virtual', sala_id=sala_id)
        
        try:
            pontos_necessarios = int(pontos_necessarios)
            missoes_necessarias = int(missoes_necessarias)
            
            if pontos_necessarios < 0 or missoes_necessarias < 0:
                raise ValueError("Valores não podem ser negativos")
            
            if pontos_necessarios == 0 and missoes_necessarias == 0:
                messages.error(request, 'O título deve ter pelo menos um requisito (pontos ou missões).')
                return redirect('usuarios:sala_virtual', sala_id=sala_id)
                
        except ValueError:
            messages.error(request, 'Valores de pontos e missões devem ser números válidos.')
            return redirect('usuarios:sala_virtual', sala_id=sala_id)
        
        # Criar título
        titulo = Titulo.objects.create(
            nome=nome,
            descricao=descricao,
            tipo='sala',
            pontos_necessarios=pontos_necessarios,
            missoes_necessarias=missoes_necessarias,
            icone=icone
        )
        
        messages.success(request, f'Título "{titulo.nome}" criado com sucesso!')
        
        # Verificar se algum aluno já merece este título
        alunos_sala = ParticipacaoSala.objects.filter(sala=sala, tipo_na_sala='aluno')
        novos_titulos = 0
        
        for part in alunos_sala:
            pontos = part.calcular_pontos_na_sala()
            missoes = part.missoes_completadas_na_sala()
            
            if pontos >= titulo.pontos_necessarios and missoes >= titulo.missoes_necessarias:
                part.titulos_sala.add(titulo)
                novos_titulos += 1
        
        if novos_titulos > 0:
            messages.info(request, f'{novos_titulos} aluno(s) conquistaram este título automaticamente!')
        
        return redirect('usuarios:sala_virtual', sala_id=sala_id)
    
    return redirect('usuarios:sala_virtual', sala_id=sala_id)


@login_required
def criar_titulo_global(request):
    """
    Permite que admins criem títulos globais.
    Apenas superusuários podem criar títulos globais.
    """
    if not request.user.is_superuser:
        messages.error(request, 'Apenas administradores podem criar títulos globais.')
        return redirect('usuarios:pag_principal')
    
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        pontos_necessarios = request.POST.get('pontos_necessarios', 0)
        missoes_necessarias = request.POST.get('missoes_necessarias', 0)
        icone = request.FILES.get('icone')
        
        # Validações
        if not nome or not descricao:
            messages.error(request, 'Nome e descrição são obrigatórios.')
            return redirect('usuarios:painel_adm')
        
        try:
            pontos_necessarios = int(pontos_necessarios)
            missoes_necessarias = int(missoes_necessarias)
            
            if pontos_necessarios < 0 or missoes_necessarias < 0:
                raise ValueError("Valores não podem ser negativos")
            
            if pontos_necessarios == 0 and missoes_necessarias == 0:
                messages.error(request, 'O título deve ter pelo menos um requisito.')
                return redirect('usuarios:painel_adm')
                
        except ValueError:
            messages.error(request, 'Valores de pontos e missões devem ser números válidos.')
            return redirect('usuarios:painel_adm')
        
        # Criar título
        titulo = Titulo.objects.create(
            nome=nome,
            descricao=descricao,
            tipo='global',
            pontos_necessarios=pontos_necessarios,
            missoes_necessarias=missoes_necessarias,
            icone=icone
        )
        
        messages.success(request, f'Título global "{titulo.nome}" criado com sucesso!')
        
        # Verificar todos os usuários
        usuarios = Usuario.objects.all()
        novos_titulos = 0
        
        for usuario in usuarios:
            if usuario.pontos_totais >= titulo.pontos_necessarios and \
               usuario.missoes_completadas_globais() >= titulo.missoes_necessarias:
                usuario.titulos_globais.add(titulo)
                novos_titulos += 1
        
        if novos_titulos > 0:
            messages.info(request, f'{novos_titulos} usuário(s) conquistaram este título!')
        
        return redirect('usuarios:painel_adm')
    
    return redirect('usuarios:painel_adm')


@login_required
def excluir_titulo(request, titulo_id):
    """
    Permite excluir um título.
    - Admins podem excluir títulos globais
    - Professores podem excluir títulos de suas salas
    """
    titulo = get_object_or_404(Titulo, id=titulo_id)
    
    # Verificar permissões
    pode_excluir = False
    redirect_url = 'usuarios:pag_principal'
    
    if titulo.tipo == 'global':
        if request.user.is_superuser:
            pode_excluir = True
            redirect_url = 'usuarios:painel_adm'
    else:  # titulo de sala
        # Verificar se é professor em alguma sala que usa este título
        # (na prática, títulos de sala não são vinculados a salas específicas no modelo atual,
        # então qualquer professor pode criar/excluir - você pode querer ajustar isso)
        participacoes_prof = ParticipacaoSala.objects.filter(
            usuario=request.user,
            tipo_na_sala='professor'
        )
        if participacoes_prof.exists():
            pode_excluir = True
            # Pegar primeira sala do professor
            redirect_url = f"usuarios:sala_virtual", participacoes_prof.first().sala.id
    
    if not pode_excluir:
        messages.error(request, 'Você não tem permissão para excluir este título.')
        return redirect('usuarios:pag_principal')
    
    if request.method == 'POST':
        nome_titulo = titulo.nome
        titulo.delete()
        messages.success(request, f'Título "{nome_titulo}" excluído com sucesso.')
    
    return redirect(redirect_url)