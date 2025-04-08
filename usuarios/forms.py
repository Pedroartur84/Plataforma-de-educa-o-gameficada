from django import forms
from . models import Usuario

class usuario(forms.ModelForm): # formulario para cadastro e login
    class Meta:
        model = Usuario
        fields = ['email', 'password', 'username']