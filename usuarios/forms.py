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