# usuarios/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import random
import string
from django.db.models.signals import post_save
from django.dispatch import receiver


# ==============================
# MODELOS DISPONÍVEIS NESTE ARQUIVO
# ==============================
# - Usuario: Modelo de usuário customizado com tipos (aluno, professor, admin)
# - Sala: Representa uma sala de aula virtual criada por usuários
# - ParticipacaoSala: Define a participação de um usuário em uma sala (professor ou aluno)
# - Missao: Missões criadas pelos professores em uma sala
# - AnexoMissao: Anexos associados às missões
# - MensagemMissao: Mensagens no chat específico da missão (comentários, entregas, correções)
# - correcaoMissao: Registros de correção das missões pelos professores
# - ChatMessage: Mensagens gerais do chat da sala virtual
# - CustomUserManager: Manager customizado para criação de usuários


# ==============================
# MANAGER E USUÁRIO CUSTOMIZADO
# ==============================
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, tipo_usuario, **extra_fields):
        if not email:
            raise ValueError('O campo E-mail é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, tipo_usuario=tipo_usuario, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, tipo_usuario='admin', **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, tipo_usuario, **extra_fields)


class Usuario(AbstractUser):
    tipo_usuario = models.CharField(
        max_length=20,
        choices=[
            ('aluno', 'Aluno'),
            ('professor', 'Professor'),
            ('admin', 'Admin')
        ],
        default='aluno',
        verbose_name="Tipo de Usuário"
    )

    username = None  # Removido
    email = models.EmailField(unique=True, verbose_name='E-mail')
    pontos_totais = models.IntegerField(default=0, verbose_name="Pontos Totais")
    foto = models.ImageField(upload_to='perfis/', blank=True, null=True, verbose_name="Foto de Perfil")
    titulos_globais = models.ManyToManyField('Titulo', blank=True, related_name='usuarios_com_titulo', limit_choices_to={'tipo': 'global'})

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['tipo_usuario']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_nome_exibicao(self):
        if self.get_full_name().strip():
            return self.get_full_name()
        nome = self.email.split('@')[0]
        return nome.replace('.', ' ').replace('_', ' ').title()

    def verificar_titulos_globais(self):
        """Verifica e concede títulos globais baseados nos pontos totais e missões completadas."""
        titulos_possiveis = Titulo.objects.filter(tipo='global')
        for titulo in titulos_possiveis:
            if (self.pontos_totais >= titulo.pontos_necessarios and
                self.missoes_completadas_globais() >= titulo.missoes_necessarias and
                titulo not in self.titulos_globais.all()):
                self.titulos_globais.add(titulo)

    def missoes_completadas_globais(self):
        """Conta missões completadas em todas as salas."""
        return correcaoMissao.objects.filter(aluno=self, pontos_atingidos__gt=0).count()

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'


# ==============================
# TÍTULO (recompensas automáticas)
# ==============================
class Titulo(models.Model):
    TIPO_CHOICES = [
        ('global', 'Global'),
        ('sala', 'Sala'),
    ]

    nome = models.CharField(max_length=100, verbose_name="Nome do Título")
    descricao = models.TextField(verbose_name="Descrição")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='global', verbose_name="Tipo")
    pontos_necessarios = models.IntegerField(default=0, verbose_name="Pontos Necessários")
    missoes_necessarias = models.IntegerField(default=0, verbose_name="Missões Completadas Necessárias")
    icone = models.ImageField(upload_to='titulos/', blank=True, null=True, verbose_name="Ícone do Título")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Título'
        verbose_name_plural = 'Títulos'


# ==============================
# SALA (qualquer usuário cria e escolhe seu papel)
# ==============================
class Sala(models.Model):
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True, null=True)
    criador = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='salas_criadas'
    )
    codigo = models.CharField(max_length=10, unique=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        super().save(*args, **kwargs)

    def professores(self):
        """Retorna todos os usuários que são professores nesta sala"""
        return Usuario.objects.filter(participacao__sala=self, participacao__tipo_na_sala='professor')

    def alunos(self):
        """Retorna todos os usuários que são alunos nesta sala"""
        return Usuario.objects.filter(participacao__sala=self, participacao__tipo_na_sala='aluno')

    def __str__(self):
        return f"{self.nome} (Código: {self.codigo})"


# ==============================
# PARTICIPAÇÃO NA SALA (aqui define se é professor ou aluno)
# ==============================
class ParticipacaoSala(models.Model):
    TIPO_CHOICES = [
        ('professor', 'Professor'),
        ('aluno', 'Aluno'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='participacao')
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='participantes')
    tipo_na_sala = models.CharField(max_length=10, choices=TIPO_CHOICES, default='aluno')
    data_entrada = models.DateTimeField(auto_now_add=True)
    titulos_sala = models.ManyToManyField(Titulo, blank=True, related_name='participacoes_com_titulo', limit_choices_to={'tipo': 'sala'})

    class Meta:
        unique_together = ('usuario', 'sala')
        verbose_name = 'Participação na Sala'
        verbose_name_plural = 'Participações nas Salas'

    def __str__(self):
        return f"{self.usuario.get_nome_exibicao()} → {self.sala} ({self.get_tipo_na_sala_display()})"

    def verificar_titulos_sala(self):
        """Verifica e concede títulos específicos da sala."""
        titulos_possiveis = Titulo.objects.filter(tipo='sala')
        pontos_na_sala = self.calcular_pontos_na_sala()
        missoes_completadas_sala = self.missoes_completadas_na_sala()
        for titulo in titulos_possiveis:
            if (pontos_na_sala >= titulo.pontos_necessarios and
                missoes_completadas_sala >= titulo.missoes_necessarias and
                titulo not in self.titulos_sala.all()):
                self.titulos_sala.add(titulo)

    def calcular_pontos_na_sala(self):
        """Calcula pontos ganhos nesta sala."""
        return correcaoMissao.objects.filter(aluno=self.usuario, missao__sala=self.sala).aggregate(models.Sum('pontos_atingidos'))['pontos_atingidos__sum'] or 0

    def missoes_completadas_na_sala(self):
        """Conta missões completadas nesta sala."""
        return correcaoMissao.objects.filter(aluno=self.usuario, missao__sala=self.sala, pontos_atingidos__gt=0).count()


# ==============================
# MISSÃO (só quem é professor na sala pode criar)
# ==============================
class Missao(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('concluida', 'Concluída'),
        ('corrigida', 'Corrigida'),
    ]

    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='missoes')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    pontos = models.IntegerField(default=10)
    data_criacao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    pontos_atingidos = models.IntegerField(default=0, blank=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Missão'
        verbose_name_plural = 'Missões'


# ==============================
# ANEXO DA MISSÃO
# ==============================
class AnexoMissao(models.Model):
    missao = models.ForeignKey(Missao, on_delete=models.CASCADE, related_name='anexos')
    arquivo = models.FileField(upload_to='anexos_missoes/')
    nome = models.CharField(max_length=255, blank=True, null=True)
    data_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome or self.arquivo.name

    class Meta:
        verbose_name = 'Anexo da Missão'
        verbose_name_plural = 'Anexos das Missões'


# ==============================
# MENSAGEM NO CHAT DA MISSÃO
# ==============================
class MensagemMissao(models.Model):
    TIPO_CHOICES = [
        ('comentario', 'Comentário'),
        ('entrega', 'Entrega'),
        ('correcao', 'Correção'),
    ]
    
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='comentario')
    
    missao = models.ForeignKey(Missao, on_delete=models.CASCADE, related_name='mensagens')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensagens_enviadas')
    texto = models.TextField()
    arquivo = models.FileField(upload_to='respostas/', blank=True, null=True)
    data_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} em {self.missao.titulo[:30]}"

    class Meta:
        ordering = ['data_envio']
        verbose_name = 'Mensagem da Missão'
        verbose_name_plural = 'Mensagens das Missões'
        
# ==============================
# CORREÇÃO DA MISSÃO]
# ==============================
class correcaoMissao(models.Model):
    missao = models.ForeignKey(Missao, on_delete=models.CASCADE, related_name='correcoes')
    aluno = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='correcoes_recebidas')
    professor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='correcoes_feitas')
    
    pontos_atingidos = models.IntegerField()
    data_correcao = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ('missao', 'aluno')
        verbose_name = 'Correção da Missão'
        verbose_name_plural = 'Correções das Missões'


class ChatMessage(models.Model):
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='chat_messages')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='chat_messages')
    texto = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['criado_em']
        verbose_name = 'Mensagem de Chat'
        verbose_name_plural = 'Mensagens de Chat'

    def __str__(self):
        return f"{self.usuario.get_nome_exibicao()} @ {self.sala.nome}: {self.texto[:30]}"


# ==============================
# SIGNALS PARA CONCESSÃO AUTOMÁTICA DE TÍTULOS
# ==============================
@receiver(post_save, sender=correcaoMissao)
def conceder_titulos_apos_correcao(sender, instance, **kwargs):
    """Após corrigir uma missão, verifica se o aluno ganhou títulos."""
    aluno = instance.aluno
    sala = instance.missao.sala

    # Verificar títulos globais
    aluno.verificar_titulos_globais()

    # Verificar títulos da sala
    try:
        participacao = ParticipacaoSala.objects.get(usuario=aluno, sala=sala)
        participacao.verificar_titulos_sala()
    except ParticipacaoSala.DoesNotExist:
        pass