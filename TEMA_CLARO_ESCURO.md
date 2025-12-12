# Modo Claro/Escuro - Documentação

## 📱 Visão Geral

A plataforma agora suporta **modo claro** e **modo escuro**, com alternância em tempo real e persistência de preferências do usuário.

## 🎯 Recursos

✅ **Toggle Fácil**: Botão na navbar para alternar entre temas
✅ **Persistência**: Preferência salva em localStorage
✅ **Sincronização com Sistema**: Respeita preferência do SO se não houver preferência salva
✅ **Transições Suaves**: Mudanças de cor com animações
✅ **Responsivo**: Funciona perfeitamente em mobile e desktop
✅ **Acessível**: Suporte ARIA para leitores de tela

## 📁 Arquivos Criados/Modificados

### Novos Arquivos:
- **`static/js/theme-toggle.js`** - Script de gerenciamento de temas
- **`static/styles/light-mode.css`** - Estilos do tema claro

### Arquivos Modificados:
- **`templates/base.html`** - Adicionado link ao light-mode.css e script theme-toggle.js
- **`templates/principal/principal_page.html`** - Adicionado botão de toggle na navbar
- **`static/styles/style.css`** - Estilos para o botão de tema

## 🔧 Como Funciona

### 1. **Inicialização**
O script `theme-toggle.js` detecta:
- Tema salvo no localStorage
- Preferência do sistema operacional
- Aplicar o tema apropriado ao carregar

### 2. **Armazenamento**
A chave de armazenamento é: `plataforma-theme`
- Valores: `'dark'` ou `'light'`
- Salvo no localStorage do navegador

### 3. **Aplicação de Estilos**
O atributo `data-theme` é definido no `<html>`:
- `data-theme="dark"` - Tema escuro (padrão)
- `data-theme="light"` - Tema claro

Também adiciona classes CSS:
- `dark-mode` - Ativa o modo escuro
- `light-mode` - Ativa o modo claro

### 4. **Evento Customizado**
Ao mudar de tema, um evento é disparado:
```javascript
window.addEventListener('themeChanged', (e) => {
    console.log('Tema mudou para:', e.detail.theme);
});
```

## 🎨 Cores do Modo Claro

### Cores Primárias:
- Background: `#F5F5F5` (cinza claro)
- Cards: `#FFFFFF` (branco)
- Texto: `#1A1A1A` (cinza escuro)
- Bordas: `#E0E0E0` (cinza médio)
- Primário: `#FFC107` (amarelo - mantido)

### Componentes Específicos:
- **Formulários**: Branco com bordas cinza
- **Botões**: Amarelo em fundo branco
- **Alertas**: Cores padrão do Bootstrap ajustadas
- **Chat**: Fundo claro sem padrão
- **Navbar**: Branco com texto escuro

## 🚀 Como Usar

### Para Usuários:
1. Clique no ícone de sol/lua na navbar
2. O tema muda instantaneamente
3. A preferência é salva automaticamente

### Para Desenvolvedores:

**Acessar o tema atual:**
```javascript
const currentTheme = window.themeManager.getCurrentTheme();
console.log(currentTheme); // 'dark' ou 'light'
```

**Alternar tema manualmente:**
```javascript
window.themeManager.toggle();
```

**Definir tema específico:**
```javascript
window.themeManager.setTheme('light', true); // true = salvar
window.themeManager.setTheme('dark', false); // false = não salvar
```

**Escutar mudanças de tema:**
```javascript
window.addEventListener('themeChanged', (e) => {
    if (e.detail.theme === 'light') {
        console.log('Modo claro ativado');
    }
});
```

## 📝 Variáveis CSS

No arquivo `light-mode.css`, todas as cores são redefinidas:

```css
html.light-mode {
    --color-primary: #FFC107;
    --color-dark-bg: #F5F5F5;
    --color-dark-card: #FFFFFF;
    --color-dark-text: #1A1A1A;
    /* ... mais variáveis */
}
```

Isso garante que todos os componentes que usam variáveis CSS se adaptem automaticamente.

## ✨ Exemplos de Componentes Adaptados

✅ Navbar e offcanvas
✅ Cards e containers
✅ Formulários e inputs
✅ Botões (primário, secondary, outline)
✅ Alertas (warning, success, info, danger)
✅ Chat e mensagens
✅ Modais
✅ Tabelas
✅ Badges
✅ Links
✅ Scrollbars

## 🔄 Fallback e Compatibilidade

- **LocalStorage indisponível**: Usa preferência do SO
- **JS desativado**: Aplicar classe `dark-mode` por padrão via HTML/CSS
- **Navegadores antigos**: Funciona com degradação graciosa

## 🐛 Troubleshooting

**O tema não persiste:**
- Verificar se localStorage está habilitado
- Limpar cache do navegador

**Ícone não muda:**
- Verificar se Bootstrap Icons está carregado
- Verificar console para erros JavaScript

**Cores incorretas:**
- Limpar cache de CSS
- Verificar se light-mode.css está carregado
- Verificar ordem de carregamento dos CSS

## 📱 Testes em Diferentes Dispositivos

- ✅ Desktop (Chrome, Firefox, Safari, Edge)
- ✅ Tablet (iPad, Android)
- ✅ Mobile (iPhone, Android)
- ✅ Modo escuro do SO respeitado
- ✅ Modo claro do SO respeitado

## 🎯 Próximos Passos Opcionais

1. **Salvar preferência no banco de dados** (ao invés de localStorage)
2. **Adicionar mais temas** (além de claro/escuro)
3. **Horário automático** (modo claro durante o dia, escuro à noite)
4. **Animação de transição mais sofisticada**
5. **Customização por usuário** em settings
