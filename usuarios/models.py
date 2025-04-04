from django.db import models
from django.contrib.auth.models import AbstractUser

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
    
    