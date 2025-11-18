from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# necessario fazer as migrações para criar as tabelas no banco de dados
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, tipo_usuario, **extra_fields):
        if not email:
            raise ValueError('O campo E-mail é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, tipo_usuario=tipo_usuario, **extra_fields)
        user.set_password(password)
        user.username = email.split('@')[0] + str(user.id or 1)  # Gera username baseado no email
        user.save()
        return user

    def create_superuser(self, email, password, tipo_usuario, **extra_fields):
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
        default='aluno'
    )
    
    username = None
    email = models.EmailField(unique=True, verbose_name='E-mail')
    
    pontos_totais = models.IntegerField(default=0, verbose_name="pontos totais")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [ 'tipo_usuario' ]  # Campos obrigatórios além do email e senha
    
    objects = CustomUserManager() # usa o manager customizado
    
    def __str__(self):
        return self.email
    
    def get_nome_exibicao(self):
        return self.get_full_name() or self.email.split('@')[0].title()


class Sala(models.Model):
    nome = models.CharField(max_length=150)
    descricao = models.TextField()
    criador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='salas_criadas')
    alunos = models.ManyToManyField(Usuario, related_name='salas_participando', blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    tipo_usuario_criador = models.CharField(
        max_length=10,
        choices=[('professor', 'Professor'), ('aluno', 'Aluno')],
        default='aluno'
    )
    atualizada_em = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nome
    

class Mensagem(models.Model):
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='mensagens')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensagens')
    texto = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.email}: {self.texto[:50]}"

class Missao(models.Model):
    # opção de status da missão
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('concluida', 'Concluída'),
        ('corrigida', 'corrigida'),
    ]
    
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='missões')
    professor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='missões_criadas')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    pontos = models.IntegerField(default=10)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    # adicionando dois novos campos
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente'
    )
    pontos_atingidos = models.IntegerField(default=0) # pontos atingidos pelo aluno na missão

    def __str__(self):
        return self.titulo

class MensagemMissao(models.Model):
    missao = models.ForeignKey(Missao, on_delete=models.CASCADE, related_name='mensagens')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensagens_missao')
    texto = models.TextField()
    arquivo = models.FileField(upload_to='respostas/', blank=True, null=True)  # Para PDF/PPT
    data_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.email}: {self.texto[:50]}"