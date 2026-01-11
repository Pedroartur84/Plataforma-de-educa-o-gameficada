# 📚 Plataforma de Educação Gamificada - Projeto de TCC

## 🎓 Sobre o Projeto
Este sistema está sendo desenvolvido como **Trabalho de Conclusão de Curso (TCC)** do **Curso Técnico em Informática** pela **Grau Técnico**.

**Objetivo Principal**:  
Desenvolver uma plataforma de aprendizagem inovadora que aplica mecânicas de jogos digitais para aumentar o engajamento dos estudantes, transformando o processo educacional em uma experiência mais dinâmica e motivadora.

## 📋 Como Executar (Versão de Desenvolvimento)
Para testar a versão atual do projeto localmente:

1. Clone o repositório:
```bash
git clone https://github.com/Pedroartur84/Plataforma-de-educa-o-gameficada.git
```

2. Acesse a pasta do projeto:
```bash
cd Plataforma-de-educa-o-gameficada
```

3. Instale as dependências necessárias:
```bash
pip install django
```

4. Execute as migrações do banco de dados:
```bash
python manage.py migrate
```

5. Inicie o servidor de desenvolvimento:
```bash
python manage.py runserver
```

A plataforma estará disponível em: http://localhost:8000

A aplicação já está rodando no render:
```bash
https://player-pnce.onrender.com
```

## 📅 Informações Acadêmicas
- **Status do Projeto**: Em desenvolvimento ativo
- **Início do Desenvolvimento**: 2024
- **Orientador**: Prof. Clodoaldo Valentin

## 👨‍💻 Autor
**Pedro Artur**  
Estudante do Curso Técnico em Informática  
Grau Técnico - Turma em andamento

---

<div align="center">
  <sub>Projeto em desenvolvimento como requisito curricular para obtenção do diploma técnico.</sub>
</div>

## PWA — Convenção de Ícones

Para a versão PWA deste projeto os ícones devem seguir a convenção abaixo e ficar em `static/pwa-icons/`.

- Nomes obrigatórios iniciais (JPEGs):
  - `icon-192x192.jpg` (obrigatório)
  - `icon-512x512.jpg` (obrigatório)
- Recomendados/úteis:
  - `icon-384x384.jpg`
  - `icon-maskable-192x192.jpg` (maskable)
  - `icon-maskable-512x512.jpg` (maskable)

Observações:
- O `manifest.json` é gerado dinamicamente pela view e prioriza `static/pwa-icons/`.
- Inicialmente gere os artefatos em JPEG com a dimensão correta no nome, depois converta para PNG com fundo transparente quando possível.
- Há um comando de gerenciamento para validar/copiar ícones: execute `python manage.py validate_pwa_icons`.
- Para obter melhores resultados no Android inclua versões `maskable` com safe area centrada.

Fluxo recomendado (rápido):
1. Exporte os ícones em JPEG com os nomes acima.
2. Coloque-os em `fotos_para_app/` ou diretamente em `static/pwa-icons/`.
3. Rode `python manage.py validate_pwa_icons` — o comando copia/valida e lista os arquivos.
4. (Opcional) Converta para PNG transparente e adicione versões maskable para maior compatibilidade.

