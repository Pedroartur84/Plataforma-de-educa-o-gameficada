from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Usuario

class LoginForm(AuthenticationForm):
    """
    Formulário de login personalizado que:
    - Substitui o username padrão por email
    - Inclui opção "Lembrar-me"
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
        # Transforma o campo email em username (exigência do Django)
        self.fields['username'] = self.fields.pop('email')
        self.fields['username'].label = "E-mail"
        self.field_order = ['username', 'password', 'remember_me']

    def clean(self):
        """Validação adicional dos dados do formulário"""
        cleaned_data = super().clean()
        # Aqui você pode adicionar validações personalizadas se necessário
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
    
    
    tipo_usuario = forms.ChoiceField(
        choices=Usuario._meta.get_field('tipo_usuario').choices,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'floatingTipoUsuario'
        }),
        label='Tipo de usuário',
        required=True
    )
    
        
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'nome de usuário',
            'id': 'floatingUsername'
        }),
        label='nome de usuário',
        required=True,
        help_text='Obrigatório. 150 caracteres ou menos. Letras, dígitos e @/./+/-/_ apenas.'
    )
    
    
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome',
            'id': 'floatingFirstName'
        }),
        label="Nome",
        required=True
    )
    
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu sobrenome',
            'id': 'floatingLastName'
        }),
        label="Sobrenome",
        required=True
    )
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'tipo_usuario', 'password1', 'password2']
        labels = {
            'username': 'Nome de usuário',
            'email': 'E-mail',
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
        }
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está em uso.')
        return email
    
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nome de usuário já está em uso.')
        return username
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #reordenar campos de necessario
        self.field_order = ['username', 'email', 'first_name', 'last_name', 'tipo_usuario', 'password1', 'password2']