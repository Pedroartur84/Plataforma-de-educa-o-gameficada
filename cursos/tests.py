from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from usuarios.models import Sala
from .models import Aula, Progresso

class CursosTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email='aluno@test.com', password='test123')
        self.sala = Sala.objects.create(nome='Curso Teste', descricao='Descrição', criador=self.user)
        self.sala.alunos.add(self.user)
        self.aula = Aula.objects.create(sala=self.sala, titulo='Aula 1', conteudo='Conteúdo', ordem=1)

    def test_lista_cursos(self):
        self.client.login(email='aluno@test.com', password='test123')
        response = self.client.get(reverse('cursos:lista_cursos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.sala.nome)

    def test_detalhe_curso(self):
        self.client.login(email='aluno@test.com', password='test123')
        response = self.client.get(reverse('cursos:detalhe_curso', args=[self.sala.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.aula.titulo)

    def test_marcar_aula_concluida(self):
        self.client.login(email='aluno@test.com', password='test123')
        response = self.client.get(reverse('cursos:marcar_aula_concluida', args=[self.aula.id]))
        self.assertRedirects(response, reverse('cursos:detalhe_curso', args=[self.sala.id]))
        self.assertTrue(self.aula.concluida_por.filter(id=self.user.id).exists())