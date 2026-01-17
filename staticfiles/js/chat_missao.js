// chat_missao.js
// Depende das variáveis globais: MISSÃO_CHAT_MESSAGES_URL, CURRENT_USER_ID

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function renderMessages(container, messages) {
    container.innerHTML = '';
    if (messages.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'text-center text-muted py-5';
        empty.innerHTML = '<i class="bi bi-chat-dots fs-4 opacity-50"></i><p class="mt-2">Nenhuma mensagem ainda</p>';
        container.appendChild(empty);
        return;
    }
    messages.forEach(m => {
        const item = document.createElement('div');
        item.className = 'chat-message mb-3';
        if (m.usuario_id == CURRENT_USER_ID) {
            item.classList.add('text-end');
        }
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble d-inline-block';
        bubble.style.borderRadius = '18px';
        bubble.style.padding = '10px 14px';

        // Definir cor baseada no tipo
        if (m.tipo === 'entrega') {
            bubble.classList.add('bg-success', 'text-white');
        } else if (m.tipo === 'correcao') {
            bubble.classList.add('bg-warning', 'text-dark');
        } else if (m.usuario_id == CURRENT_USER_ID) {
            bubble.classList.add('bg-primary', 'text-white');
        } else {
            bubble.classList.add('bg-secondary', 'text-white');
        }

        const header = document.createElement('div');
        header.className = 'd-flex justify-content-between align-items-start gap-2 mb-1';
        const name = document.createElement('strong');
        name.className = 'small';
        name.textContent = m.usuario_nome;
        if (m.tipo === 'entrega') {
            const badge = document.createElement('span');
            badge.className = 'badge bg-dark ms-1';
            badge.textContent = 'ENTREGA';
            name.appendChild(badge);
        } else if (m.tipo === 'correcao') {
            const badge = document.createElement('span');
            badge.className = 'badge bg-dark ms-1';
            badge.textContent = 'CORREÇÃO';
            name.appendChild(badge);
        }
        const time = document.createElement('small');
        time.className = 'text-muted opacity-75';
        time.textContent = new Date(m.data_envio).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        header.appendChild(name);
        header.appendChild(time);

        bubble.appendChild(header);

        if (m.texto) {
            const text = document.createElement('p');
            text.className = 'mb-2 small';
            text.innerHTML = m.texto.replace(/\n/g, '<br>');
            bubble.appendChild(text);
        }

        if (m.arquivo) {
            const fileDiv = document.createElement('div');
            fileDiv.className = 'mt-2';
            const link = document.createElement('a');
            link.href = m.arquivo;
            link.target = '_blank';
            link.className = 'btn btn-sm btn-outline-light';
            link.innerHTML = '<i class="bi bi-download"></i> Arquivo';
            fileDiv.appendChild(link);
            bubble.appendChild(fileDiv);
        }

        item.appendChild(bubble);
        container.appendChild(item);
    });
    // rolar para baixo
    container.scrollTop = container.scrollHeight;
}

async function fetchMessages(container) {
    try {
        const res = await fetch(MISSAO_CHAT_MESSAGES_URL, { credentials: 'same-origin' });
        if (!res.ok) return;
        const data = await res.json();
        renderMessages(container, data);
    } catch (err) {
        console.error('Erro ao buscar mensagens', err);
    }
}

function initMissaoChat() {
    const container = document.getElementById('missao-chat-messages');
    if (!container) return;

    // buscar mensagens imediatamente
    fetchMessages(container);
    // polling
    setInterval(() => fetchMessages(container), 3000);
}

// Automatic init when script é carregado (espera que variáveis globais existam)
window.addEventListener('DOMContentLoaded', () => {
    if (typeof MISSAO_CHAT_MESSAGES_URL === 'undefined') return;
    initMissaoChat();
});