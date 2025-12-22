# cursos/models.py
from django.db import models
from usuarios.models import Usuario, Sala, Missao

# ==============================
# MODELS ANTIGOS (manter por compatibilidade)
# ==============================
class Aula(models.Model):
    """DEPRECATED - Manter apenas para compatibilidade com dados antigos"""
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='aulas')
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField(blank=True)
    ordem = models.IntegerField(default=0)
    concluida_por = models.ManyToManyField(Usuario, related_name='aulas_concluidas', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return f"{self.titulo} (Sala: {self.sala.nome})"


class Progresso(models.Model):
    """DEPRECATED - Manter apenas para compatibilidade"""
    aluno = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='progressos')
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='progressos')
    percentual = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('aluno', 'sala')

    def __str__(self):
        return f"{self.aluno.email} - {self.sala.nome}: {self.percentual}%"


# ==============================
# NOVO SISTEMA DE TRILHAS
# ==============================
class Trilha(models.Model):
    """
    Sequência estruturada de aprendizado dentro de uma sala.
    Pode ter requisitos para ser desbloqueada.
    """
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='trilhas')
    nome = models.CharField(max_length=200, verbose_name="Nome da Trilha")
    descricao = models.TextField(verbose_name="Descrição")
    ordem = models.IntegerField(default=0, verbose_name="Ordem de Exibição")
    
    # Requisitos para desbloquear
    pontos_necessarios = models.IntegerField(
        default=0, 
        verbose_name="Pontos Necessários",
        help_text="Pontos totais que o aluno precisa ter para acessar"
    )
    trilha_anterior = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        verbose_name="Trilha Anterior",
        help_text="Trilha que deve ser completada antes desta"
    )
    
    # Metadata
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    criador = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['ordem']
        verbose_name = 'Trilha de Aprendizado'
        verbose_name_plural = 'Trilhas de Aprendizado'
    
    def __str__(self):
        return f"{self.nome} - {self.sala.nome}"
    
    def total_conteudos(self):
        """Retorna o número total de conteúdos nesta trilha"""
        return ConteudoModulo.objects.filter(modulo__trilha=self).count()
    
    def conteudos_completos_usuario(self, usuario):
        """Retorna quantos conteúdos o usuário completou"""
        return VisualizacaoConteudo.objects.filter(
            usuario=usuario,
            conteudo__modulo__trilha=self,
            completo=True
        ).count()
    
    def progresso_usuario(self, usuario):
        """Retorna o percentual de progresso do usuário (0-100)"""
        total = self.total_conteudos()
        if total == 0:
            return 0
        completos = self.conteudos_completos_usuario(usuario)
        return round((completos / total) * 100, 1)
    
    def esta_desbloqueada_para(self, usuario):
        """Verifica se a trilha está desbloqueada para o usuário"""
        # Verificar pontos
        if self.pontos_necessarios > 0:
            if usuario.pontos_totais < self.pontos_necessarios:
                return False
        
        # Verificar trilha anterior
        if self.trilha_anterior:
            total_anterior = self.trilha_anterior.total_conteudos()
            completos_anterior = self.trilha_anterior.conteudos_completos_usuario(usuario)
            if total_anterior > 0 and completos_anterior < total_anterior:
                return False
        
        return True


class Modulo(models.Model):
    """
    Agrupamento de conteúdos dentro de uma trilha.
    Exemplo: "Módulo 1: Introdução", "Módulo 2: Conceitos Avançados"
    """
    trilha = models.ForeignKey(Trilha, on_delete=models.CASCADE, related_name='modulos')
    titulo = models.CharField(max_length=200, verbose_name="Título do Módulo")
    descricao = models.TextField(verbose_name="Descrição", blank=True)
    ordem = models.IntegerField(default=0, verbose_name="Ordem")
    
    # Relacionar com missões existentes (opcional)
    missoes = models.ManyToManyField(
        Missao, 
        blank=True,
        verbose_name="Missões Relacionadas",
        help_text="Missões que fazem parte deste módulo"
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['ordem']
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'
    
    def __str__(self):
        return f"{self.titulo} ({self.trilha.nome})"
    
    def total_conteudos(self):
        """Retorna o número de conteúdos neste módulo"""
        return self.conteudos.count()
    
    def progresso_usuario(self, usuario):
        """Retorna o percentual de progresso do usuário neste módulo"""
        total = self.total_conteudos()
        if total == 0:
            return 0
        completos = VisualizacaoConteudo.objects.filter(
            usuario=usuario,
            conteudo__modulo=self,
            completo=True
        ).count()
        return round((completos / total) * 100, 1)


class ConteudoModulo(models.Model):
    """
    Conteúdo individual dentro de um módulo.
    Pode ser texto, vídeo, arquivo ou link externo.
    """
    TIPO_CHOICES = [
        ('texto', 'Texto/Artigo'),
        ('video', 'Vídeo'),
        ('arquivo', 'Arquivo/PDF'),
        ('link', 'Link Externo'),
    ]
    
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='conteudos')
    titulo = models.CharField(max_length=200, verbose_name="Título")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name="Tipo de Conteúdo")
    ordem = models.IntegerField(default=0, verbose_name="Ordem")
    
    # Conteúdo (dependendo do tipo)
    conteudo = models.TextField(
        blank=True, 
        verbose_name="Conteúdo de Texto",
        help_text="Usado para tipo 'texto'"
    )
    arquivo = models.FileField(
        upload_to='conteudos/', 
        blank=True, 
        null=True,
        verbose_name="Arquivo",
        help_text="Usado para tipo 'arquivo' ou 'video'"
    )
    link = models.URLField(
        blank=True,
        verbose_name="Link Externo",
        help_text="Usado para tipo 'link' ou 'video' (YouTube, etc)"
    )
    
    # Metadata
    duracao_estimada = models.IntegerField(
        default=0,
        verbose_name="Duração Estimada (minutos)",
        help_text="Tempo estimado para completar este conteúdo"
    )
    
    # Tracking de visualização
    visualizado_por = models.ManyToManyField(
        Usuario, 
        through='VisualizacaoConteudo', 
        blank=True,
        related_name='conteudos_visualizados'
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['ordem']
        verbose_name = 'Conteúdo'
        verbose_name_plural = 'Conteúdos'
    
    def __str__(self):
        return f"{self.titulo} ({self.get_tipo_display()})"
    
    def foi_visualizado_por(self, usuario):
        """Verifica se o usuário já visualizou este conteúdo"""
        return VisualizacaoConteudo.objects.filter(
            usuario=usuario,
            conteudo=self
        ).exists()
    
    def esta_completo_para(self, usuario):
        """Verifica se o usuário marcou este conteúdo como completo"""
        viz = VisualizacaoConteudo.objects.filter(
            usuario=usuario,
            conteudo=self
        ).first()
        return viz.completo if viz else False
    
    def proximo_conteudo(self):
        """Retorna o próximo conteúdo no mesmo módulo"""
        return ConteudoModulo.objects.filter(
            modulo=self.modulo,
            ordem__gt=self.ordem
        ).first()
    
    def conteudo_anterior(self):
        """Retorna o conteúdo anterior no mesmo módulo"""
        return ConteudoModulo.objects.filter(
            modulo=self.modulo,
            ordem__lt=self.ordem
        ).last()


class VisualizacaoConteudo(models.Model):
    """
    Registra quando um aluno visualizou/completou um conteúdo.
    Tabela intermediária para tracking de progresso.
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    conteudo = models.ForeignKey(ConteudoModulo, on_delete=models.CASCADE)
    
    # Timestamps
    data_visualizacao = models.DateTimeField(auto_now_add=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)
    
    # Status
    completo = models.BooleanField(
        default=False,
        verbose_name="Marcado como Completo"
    )
    
    # Opcional: tempo gasto (para analytics futuro)
    tempo_gasto_segundos = models.IntegerField(default=0, blank=True)
    
    class Meta:
        unique_together = ('usuario', 'conteudo')
        verbose_name = 'Visualização de Conteúdo'
        verbose_name_plural = 'Visualizações de Conteúdos'
        ordering = ['-data_visualizacao']
    
    def __str__(self):
        status = "✓" if self.completo else "⏳"
        return f"{status} {self.usuario.get_nome_exibicao()} - {self.conteudo.titulo}"
        