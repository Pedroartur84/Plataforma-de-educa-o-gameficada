/* theme-toggle.js - Gerenciador de Tema Claro/Escuro */

class ThemeManager {
    constructor() {
        this.THEME_KEY = 'plataforma-theme';
        this.DARK = 'dark';
        this.LIGHT = 'light';
        this.init();
    }

    init() {
        console.log('[ThemeManager] Inicializando...');
        
        // Verificar tema salvo ou preferência do sistema
        const savedTheme = localStorage.getItem(this.THEME_KEY);
        const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? this.DARK : this.LIGHT;
        const theme = savedTheme || systemTheme;
        
        console.log('[ThemeManager] Tema salvo:', savedTheme, '| Tema sistema:', systemTheme, '| Tema a usar:', theme);
        
        this.setTheme(theme, false);
        this.setupToggleListener();
        this.observeSystemThemeChange();
    }

    setTheme(theme, save = true) {
        console.log('[ThemeManager] Definindo tema:', theme, '| Salvar:', save);
        
        const html = document.documentElement;
        const isDark = theme === this.DARK;
        
        if (isDark) {
            html.setAttribute('data-theme', this.DARK);
            html.classList.remove('light-mode');
            html.classList.add('dark-mode');
            console.log('[ThemeManager] Classes aplicadas: dark-mode');
            console.log('[ThemeManager] HTML classes:', html.className);
        } else {
            html.setAttribute('data-theme', this.LIGHT);
            html.classList.remove('dark-mode');
            html.classList.add('light-mode');
            console.log('[ThemeManager] Classes aplicadas: light-mode');
            console.log('[ThemeManager] HTML classes:', html.className);
        }

        // Força um reflow para garantir que o navegador aplique os estilos
        console.log('[ThemeManager] CSS variables atualizadas:', {
            'color-dark-bg': getComputedStyle(html).getPropertyValue('--color-dark-bg'),
            'color-dark-text': getComputedStyle(html).getPropertyValue('--color-dark-text')
        });

        // Atualizar button estado
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            console.log('[ThemeManager] Botão encontrado, atualizando...');
            toggleBtn.setAttribute('aria-pressed', isDark ? 'true' : 'false');
            const icon = toggleBtn.querySelector('i');
            if (icon) {
                const newClass = isDark ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
                icon.className = newClass;
                console.log('[ThemeManager] Ícone atualizado para:', newClass);
            }
        } else {
            console.log('[ThemeManager] Botão não encontrado!');
        }

        // Disparar evento customizado
        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));

        if (save) {
            localStorage.setItem(this.THEME_KEY, theme);
            console.log('[ThemeManager] Tema salvo em localStorage');
        }
    }

    toggle() {
        console.log('[ThemeManager] Toggle acionado');
        const current = document.documentElement.getAttribute('data-theme') || this.DARK;
        console.log('[ThemeManager] Tema atual:', current);
        const newTheme = current === this.DARK ? this.LIGHT : this.DARK;
        console.log('[ThemeManager] Novo tema:', newTheme);
        this.setTheme(newTheme, true);
    }

    setupToggleListener() {
        const btn = document.getElementById('theme-toggle');
        if (btn) {
            console.log('[ThemeManager] Adicionando listener de click ao botão');
            btn.addEventListener('click', (e) => {
                console.log('[ThemeManager] Clique detectado no botão');
                e.preventDefault();
                this.toggle();
            });
        } else {
            console.log('[ThemeManager] Botão não encontrado para setup do listener!');
        }
    }

    observeSystemThemeChange() {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addEventListener('change', (e) => {
            const savedTheme = localStorage.getItem(this.THEME_KEY);
            if (!savedTheme) {
                const newTheme = e.matches ? this.DARK : this.LIGHT;
                this.setTheme(newTheme, false);
            }
        });
    }

    getCurrentTheme() {
        return document.documentElement.getAttribute('data-theme') || this.DARK;
    }
}

// Inicializar tema quando DOM está pronto
function initThemeManager() {
    console.log('[ThemeManager] Iniciando ThemeManager...');
    window.themeManager = new ThemeManager();
    console.log('[ThemeManager] ThemeManager inicializado com sucesso');
}

if (document.readyState === 'loading') {
    console.log('[ThemeManager] DOM ainda está carregando, aguardando...');
    document.addEventListener('DOMContentLoaded', initThemeManager);
} else {
    console.log('[ThemeManager] DOM já está pronto');
    initThemeManager();
}
