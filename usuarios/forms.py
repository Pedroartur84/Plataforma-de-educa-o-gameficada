from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Usuario, Sala, Missao, MensagemMissao
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
        fields = ['nome', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da sala'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
        
class MissaoForm(forms.ModelForm):
    class Meta:
        model = Missao
        fields = ['titulo', 'descricao', 'pontos']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'pontos': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
        }
        

class MensagemMissaoForm(forms.ModelForm):
    class Meta:
        model = MensagemMissao
        fields = ['texto', 'arquivo']
        widgets = {
            'texto': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        

class CorrecaoMissaoForm(forms.Form):
    pontos_atingidos = forms.IntegerField(
        min_value=0,
        max_value=10,
        label='pontos atribuidos (0-10)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10, 'required': True})
    )


class PerfilForm(forms.ModelForm):
    """
    Formulário para edição de perfil do usuário.
    Permite alterar nome, sobrenome e foto.
    """
    
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'foto']
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'foto': 'Foto de Perfil',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control input-estilo bg-dark text-white',
                'placeholder': 'Seu nome',
                'maxlength': 150,
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control input-estilo bg-dark text-white',
                'placeholder': 'Seu sobrenome',
                'maxlength': 150,
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-control input-estilo bg-dark text-white',
                'accept': 'image/jpeg,image/png,image/jpg',
            }),
        }
    
    def clean_foto(self):
        """
        Valida o arquivo de foto enviado.
        Limita tamanho e formatos aceitos.
        """
        foto = self.cleaned_data.get('foto')
        
        if foto:
            # Verifica tamanho (5MB máximo)
            if foto.size > 5 * 1024 * 1024:  # 5MB em bytes
                raise forms.ValidationError(
                    'A foto deve ter no máximo 5MB.'
                )
            
            # Verifica tipo de arquivo
            valid_types = ['image/jpeg', 'image/jpg', 'image/png']
            if foto.content_type not in valid_types:
                raise forms.ValidationError(
                    'Formato inválido. Use JPG ou PNG.'
                )
        
        return foto
    
    def clean_first_name(self):
        """Remove espaços extras do nome"""
        first_name = self.cleaned_data.get('first_name', '')
        return first_name.strip()
    
    def clean_last_name(self):
        """Remove espaços extras do sobrenome"""
        last_name = self.cleaned_data.get('last_name', '')
        return last_name.strip()