from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Usuario
from .models import *

class LoginForm(AuthenticationForm):
    """
    Formulário de login personalizado que:
    Substitui o username padrão por email
    """
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com',
            'id': 'floatingInput'
        }),
        label="E-mail",
        required=True
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha',
            'id': 'floatingPassword'
        }),
        label="Senha",
        required=True
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input', 
            'id': 'flexCheckDefault'
        }),
        label="Lembrar-me"
    )

    def __init__(self, *args, **kwargs):
        """Configuração inicial que adapta o email para o sistema de autenticação do Django"""
        super().__init__(*args, **kwargs)
        # Transforma o campo email em username
        self.fields['username'] = self.fields.pop('email')
        self.fields['username'].label = "E-mail"
        self.field_order = ['username', 'password', 'remember_me']

    def clean(self):
        """Validação adicional dos dados do formulário"""
        cleaned_data = super().clean()
        return cleaned_data
    
    
class CadastroForm(UserCreationForm):
    """
    formulario de cadastro de usuario
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com',
            'id': 'floatingEmail'
        }),
        label='E-mail',
        required=True
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha',
            'id': 'floatingPassword1'
        }),
        label='Senha',
        required=True
    )
    
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Comfirme sua senha',
            'id': 'floatingPassword2'
        }),
        label='Comfirmação de senha',
        required=True
    )
    
    class Meta:
        model = Usuario
        fields = ['email', 'password1', 'password2']
        labels = {
            'email': 'E-mail',
        }
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está em uso.')
        return email
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #reordenar campos de necessario
        self.field_pop = ['username', None]
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
        
class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['nome', 'descricao', 'tipo_usuario_criador']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'required': True , 'rows': 3}),
            'tipo_usuario_criador': forms.Select(attrs={'class': 'form-control', 'required': True}),
        }
        
        
class MensagemForm(forms.ModelForm):
    class Meta:
        model = Mensagem
        fields = ['texto']
        widgets = {
            'texto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua mensagem...', 'required': True}),
        }
        
        
class MissaoForm(forms.ModelForm):
    class Meta:
        model = Missao
        fields = ['titulo', 'descricao', 'pontos']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título da missão', 'required': True}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descrição da missão', 'required': True, 'rows': 3}),
            'pontos': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'pontos (máimo 10)',
                'min': 1,
                'max': 10, # limitar pontos entre 1 e 10
                'required': True
            })
        }
        
    def clean_pontos(self):
        """Validação para garantir que os pontos estejam entre 1 e 10"""
        pontos = self.cleaned_data.get('pontos')
        if pontos and (pontos < 1 or pontos > 10):
            raise forms.ValidationError('Os pontos devem estar entre 1 e 10.')
        if pontos and pontos < 1:
            raise forms.ValidationError('Os pontos devem ser no mínimo 1.')
        return pontos
        

class MensagemMissaoForm(forms.ModelForm):
    class Meta:
        model = MensagemMissao
        fields = ['texto', 'arquivo']
        widgets = {
            'texto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua resposta...', 'required': True}),
            'arquivo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
        

class CorrecaoMissaoForm(forms.Form):
    pontos_atingidos = forms.IntegerField(
        min_value=0,
        max_value=10,
        label='pontos atribuidos (0-10)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10, 'required': True})
    )