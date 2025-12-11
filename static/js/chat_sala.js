// chat_sala.js
// Depende das variáveis globais: CHAT_MESSAGES_URL, CURRENT_USER_ID, CURRENT_USER_NAME

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function renderMessages(container, messages) {
    container.innerHTML = '';
    messages.forEach(m => {
        const item = document.createElement('div');
        item.className = 'chat-message mb-2';
        const author = document.createElement('div');
        author.className = 'small text-white-50';
        author.textContent = `${m.usuario_nome} • ${new Date(m.criado_em).toLocaleString()}`;
        const text = document.createElement('div');
        text.className = 'text-white';
        text.textContent = m.texto;
        item.appendChild(author);
        item.appendChild(text);
        container.appendChild(item);
    });
    // rolar para baixo
    container.scrollTop = container.scrollHeight;
}

async function fetchMessages(container) {
    try {
        const res = await fetch(CHAT_MESSAGES_URL, { credentials: 'same-origin' });
        if (!res.ok) return;
        const data = await res.json();
        renderMessages(container, data);
    } catch (err) {
        console.error('Erro ao buscar mensagens', err);
    }
}

async function sendMessage(inputEl, container) {
    const texto = inputEl.value.trim();
    if (!texto) return;
    const csrftoken = getCookie('csrftoken');
    try {
        const res = await fetch(CHAT_MESSAGES_URL, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({ texto }),
        });
        if (res.status === 201) {
            inputEl.value = '';
            // recarregar mensagens
            await fetchMessages(container);
        } else {
            console.error('Erro ao enviar mensagem', res.status);
        }
    } catch (err) {
        console.error('Erro ao enviar mensagem', err);
    }
}

function initSalaChat() {
    const container = document.getElementById('sala-chat-messages');
    const input = document.getElementById('sala-chat-input');
    const sendBtn = document.getElementById('sala-chat-send');
    if (!container || !input || !sendBtn) return;

    // buscar mensagens imediatamente
    fetchMessages(container);
    // polling
    setInterval(() => fetchMessages(container), 3000);

    sendBtn.addEventListener('click', (e) => {
        e.preventDefault();
        sendMessage(input, container);
    });

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage(input, container);
        }
    });
}

// Automatic init when script é carregado (espera que variáveis globais existam)
window.addEventListener('DOMContentLoaded', () => {
    if (typeof CHAT_MESSAGES_URL === 'undefined') return;
    initSalaChat();
});
