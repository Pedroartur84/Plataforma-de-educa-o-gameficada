from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from usuarios.models import Usuario

# Register your models here.
class UsuarioAdminConfig(UserAdmin):
    # configuração da lista
    list_display = ('email', 'first_name', 'last_name', 'tipo_usuario', 'is_active', 'is_staff')
    
    # campos para filtros
    list_filter = ('tipo_usuario', 'is_active', 'is_staff')
    
    # campos pesquisáveis
    search_fields = ('email', 'first_name', 'last_name')
    
    # ordenação padão
    ordering = ('-date_joined',)
    
    # comfiguração dos campos no formulario
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name')}),
        ('Permissões', {
            'fields': ('tipo_usuario', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    # configuração do formulario de adição 
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'tipo_usuario', 'password1', 'password2', 'is_active', 'is_staff')}
        ),
    )
    
    # registar o modelo com a configuração personalizada
admin.site.register(Usuario, UsuarioAdminConfig)

