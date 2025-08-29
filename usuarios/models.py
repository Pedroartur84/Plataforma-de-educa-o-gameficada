from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# necesario fazer as migrações para criar as tabelas no banco de dados
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
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [ 'tipo_usuario' ]  # Campos obrigatórios além do email e senha
    
    objects = CustomUserManager() # usa o manager customizado
    
    def __str__(self):
        return self.email


class Sala(models.Model):
    nome = models.CharField(max_length=150)
    descricao = models.TextField()
    criador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='salas_criadas')
    alunos = models.ManyToManyField(Usuario, related_name='salas_participando', blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nome