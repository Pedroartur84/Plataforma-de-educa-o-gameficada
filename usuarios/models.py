from django.db import models
from django.contrib.auth.models import AbstractUser

# necesario fazer as migrações para criar as tabelas no banco de dados
# Create your models here.
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
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email


class Sala(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    criador = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    data_criacao = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.nome