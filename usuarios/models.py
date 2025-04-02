from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class usuario(AbstractUser):
    tipo_usuario = models.charfiel(
        max_length=20,
        choices=[
            ('aluno', 'aluno'),
            ('profesor','profesor'),
            ('admin', 'admin')
        ]
        choices=tipos_usuario,
        default='aluno'
        #aluno sera o valor padrão
    )