from django.db import models
from usuarios.models import Usuario, Sala

# Create your models here.
class aula(models.Model):
    Sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='aulas')
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField(blank=True) #para texto ou links
    ordem = models.IntegerField(default=0) #ordem da trilha
    concluida_por = models.ManyToManyField(Usuario, related_name='aulas_concluidas', blank=True) #progresso do aluno
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['ordem']
        
    def __str__(self):
        return f"{self.titulo} (sala: {self.Sala.nome})"
    
    class progresso(models.Model):
        aluno = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='progresso')
        Sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='progresso')
        percentual = models.FloatField(default=0.0) #percentual de conclusão da sala
    
        class Meta:
            unique_together = ('aluno', 'Sala')
            
        def __str__(self):
            return f"{self.aluno.email} - {self.Sala.nome}: {self.percentual}%"