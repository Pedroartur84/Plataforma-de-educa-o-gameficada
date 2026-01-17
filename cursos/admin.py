from django.contrib import admin

# Register your models here.

# cursos/admin.py
from django.contrib import admin
from .models import (
    Aula, Progresso,  # Antigos
    Trilha, Modulo, ConteudoModulo, VisualizacaoConteudo  # Novos
)

# ==============================
# ADMIN DOS MODELS ANTIGOS (readonly para preservar dados)
# ==============================
@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'sala', 'ordem', 'criado_em')
    list_filter = ('sala',)
    search_fields = ('titulo', 'sala__nome')
    readonly_fields = ('criado_em',)


@admin.register(Progresso)
class ProgressoAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'sala', 'percentual')
    list_filter = ('sala',)
    search_fields = ('aluno__email', 'sala__nome')


# ==============================
# ADMIN DO NOVO SISTEMA DE TRILHAS
# ==============================

class ModuloInline(admin.TabularInline):
    """Permite editar módulos diretamente na página da trilha"""
    model = Modulo
    extra = 1
    fields = ('titulo', 'descricao', 'ordem')


@admin.register(Trilha)
class TrilhaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sala', 'professor', 'ordem', 'total_conteudos', 'criado_em')
    list_filter = ('sala', 'professor', 'criado_em')
    search_fields = ('nome', 'sala__nome', 'descricao')
    readonly_fields = ('criado_em', 'atualizado_em')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('sala', 'nome', 'descricao', 'ordem')
        }),
        ('Responsável', {
            'fields': ('professor',),
            'description': 'Professor que gerencia esta trilha'
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ModuloInline]
    
    def total_conteudos(self, obj):
        """Mostra o total de conteúdos na trilha"""
        return obj.total_conteudos()
    total_conteudos.short_description = 'Total de Conteúdos'


class ConteudoModuloInline(admin.TabularInline):
    """Permite editar conteúdos diretamente na página do módulo"""
    model = ConteudoModulo
    extra = 1
    fields = ('titulo', 'tipo', 'ordem', 'duracao_estimada')


@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'trilha', 'ordem', 'total_conteudos', 'criado_em')
    list_filter = ('trilha__sala', 'trilha')
    search_fields = ('titulo', 'trilha__nome', 'descricao')
    readonly_fields = ('criado_em',)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('trilha', 'titulo', 'descricao', 'ordem')
        }),
        ('Missões Relacionadas', {
            'fields': ('missoes',),
            'description': 'Vincule missões existentes a este módulo (opcional)'
        }),
    )
    
    filter_horizontal = ('missoes',)
    inlines = [ConteudoModuloInline]
    
    def total_conteudos(self, obj):
        """Mostra o total de conteúdos no módulo"""
        return obj.total_conteudos()
    total_conteudos.short_description = 'Conteúdos'


@admin.register(ConteudoModulo)
class ConteudoModuloAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'modulo', 'tipo', 'ordem', 'duracao_estimada', 'total_visualizacoes')
    list_filter = ('tipo', 'modulo__trilha__sala', 'modulo__trilha', 'modulo')
    search_fields = ('titulo', 'modulo__titulo', 'conteudo')
    readonly_fields = ('criado_em', 'atualizado_em', 'total_visualizacoes', 'total_completos')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('modulo', 'titulo', 'tipo', 'ordem', 'duracao_estimada')
        }),
        ('Conteúdo (dependendo do tipo)', {
            'fields': ('conteudo', 'arquivo', 'link'),
            'description': 'Preencha o campo apropriado baseado no tipo selecionado'
        }),
        ('Estatísticas', {
            'fields': ('total_visualizacoes', 'total_completos'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def total_visualizacoes(self, obj):
        """Mostra quantos usuários visualizaram"""
        return VisualizacaoConteudo.objects.filter(conteudo=obj).count()
    total_visualizacoes.short_description = 'Visualizações'
    
    def total_completos(self, obj):
        """Mostra quantos usuários completaram"""
        return VisualizacaoConteudo.objects.filter(conteudo=obj, completo=True).count()
    total_completos.short_description = 'Completados'


@admin.register(VisualizacaoConteudo)
class VisualizacaoConteudoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'conteudo', 'completo', 'data_visualizacao', 'tempo_gasto_formatado')
    list_filter = ('completo', 'conteudo__modulo__trilha__sala', 'conteudo__tipo')
    search_fields = ('usuario__email', 'usuario__first_name', 'usuario__last_name', 'conteudo__titulo')
    readonly_fields = ('data_visualizacao', 'ultima_atualizacao')
    date_hierarchy = 'data_visualizacao'
    
    fieldsets = (
        ('Informações', {
            'fields': ('usuario', 'conteudo', 'completo')
        }),
        ('Timestamps', {
            'fields': ('data_visualizacao', 'ultima_atualizacao', 'tempo_gasto_segundos')
        }),
    )
    
    def tempo_gasto_formatado(self, obj):
        """Formata o tempo gasto em formato legível"""
        if obj.tempo_gasto_segundos == 0:
            return '-'
        minutos = obj.tempo_gasto_segundos // 60
        segundos = obj.tempo_gasto_segundos % 60
        return f"{minutos}m {segundos}s"
    tempo_gasto_formatado.short_description = 'Tempo Gasto'