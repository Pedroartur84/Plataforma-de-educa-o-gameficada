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
        item.className = 'chat-message mb-2 d-flex align-items-start gap-2';
        const avatar = document.createElement('div');
        avatar.className = 'flex-shrink-0';
        if (m.usuario_foto) {
            const img = document.createElement('img');
            img.src = m.usuario_foto;
            img.alt = m.usuario_nome;
            img.className = 'rounded-circle';
            img.style.width = '32px';
            img.style.height = '32px';
            img.style.objectFit = 'cover';
            avatar.appendChild(img);
        } else {
            avatar.innerHTML = '<div class="rounded-circle bg-warning text-dark d-flex align-items-center justify-content-center" style="width: 32px; height: 32px; font-size: 0.8rem;"><i class="bi bi-person"></i></div>';
        }
        const content = document.createElement('div');
        content.className = 'flex-grow-1';
        const author = document.createElement('div');
        author.className = 'small text-white-50';
        author.textContent = `${m.usuario_nome} • ${new Date(m.criado_em).toLocaleString()}`;
        const text = document.createElement('div');
        text.className = 'text-white';
        text.textContent = m.texto;
        content.appendChild(author);
        content.appendChild(text);
        item.appendChild(avatar);
        item.appendChild(content);
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
