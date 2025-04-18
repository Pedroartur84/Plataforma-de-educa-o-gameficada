from django import forms
from django.contrib.auth.forms import AuthenticationForm

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