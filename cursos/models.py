from django.db import models
from usuarios.models import Usuario, Sala

class Aula(models.Model):
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
    aluno = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='progressos')
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='progressos')
    percentual = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('aluno', 'sala')

    def __str__(self):
        return f"{self.aluno.email} - {self.sala.nome}: {self.percentual}%"
        