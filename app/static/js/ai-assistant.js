/* AI Assistant widget. Simplified functional version. */
(function () {
    'use strict';
    const API_CHAT = '/descubrir/api/recommend';
    const getApp = () => window.app;
    const el = (tag, className, text) => {
        const n = document.createElement(tag);
        if (className) n.className = className;
        if (text != null) n.textContent = text;
        return n;
    };
    function injectStyles() {
        if (document.getElementById('ai-assistant-styles')) return;
        const s = document.createElement('style');
        s.id = 'ai-assistant-styles';
        s.textContent = `
            .ai-fab { position:fixed; right:20px; bottom:20px; z-index:1200; width:58px; height:58px; border:none; border-radius:50%; cursor:pointer; color:var(--theme-text); font-size:var(--text-xl); background:linear-gradient(135deg,var(--theme-accent-bg),var(--theme-danger-bg)); box-shadow:0 8px 22px var(--theme-shadow); transition:transform .2s ease; }
            .ai-fab:hover { transform:scale(1.08); }
            .ai-chat { position:fixed; right:20px; bottom:92px; z-index:1200; width:360px; max-width:calc(100vw - 40px); height:520px; max-height:calc(100vh - 120px); display:flex; flex-direction:column; overflow:hidden; background:var(--theme-surface); border-radius:18px; box-shadow:0 18px 50px var(--theme-shadow); }
            .ai-chat-head { display:flex; align-items:center; justify-content:space-between; padding:var(--space-md); color:var(--theme-text); font-weight:700; background:linear-gradient(135deg,var(--theme-accent-bg),var(--theme-danger-bg)); }
            .ai-chat-close { border:none; background:none; color:var(--theme-text); font-size:var(--text-xl); cursor:pointer; }
            .ai-chat-body { flex:1; overflow-y:auto; padding:var(--space-md); display:flex; flex-direction:column; gap:var(--space-sm); background:var(--theme-surface); }
            .ai-bubble { max-width:85%; padding:var(--space-sm) var(--space-md); border-radius:14px; font-size:var(--text-sm); line-height:1.45; }
            .ai-bubble.bot { align-self:flex-start; background:var(--theme-surface); color:var(--theme-text); border:1px solid var(--theme-border); }
            .ai-bubble.user { align-self:flex-end; background:var(--theme-accent-bg); color:var(--theme-text); }
            .ai-chat-form { display:flex; gap:var(--space-sm); padding:var(--space-sm); border-top:1px solid var(--theme-border); background:var(--theme-surface); }
            .ai-chat-input { flex:1; min-width:0; padding:var(--space-sm) var(--space-md); border:1px solid var(--theme-border); border-radius:999px; outline:none; font-size:var(--text-sm); }
            .ai-chat-send { width:40px; height:40px; border:none; border-radius:50%; cursor:pointer; color:var(--theme-text); background:var(--theme-accent-bg); }
        `;
        document.head.appendChild(s);
    }
    function buildChat() {
        const fab = el('button', 'ai-fab');
        fab.type = 'button';
        fab.title = 'Asistente IA';
        fab.textContent = 'IA';
        fab.setAttribute('aria-label', 'Abrir asistente IA');
        const panel = el('div', 'ai-chat');
        panel.style.display = 'none';
        panel.innerHTML = `<div class="ai-chat-head"><span>Asistente SmartResto</span><button type="button" class="ai-chat-close" aria-label="Cerrar">×</button></div><div class="ai-chat-body"></div><div class="ai-chat-form"><input type="text" class="ai-chat-input" maxlength="300" placeholder="¿Qué se te antoja?"><button type="button" class="ai-chat-send" aria-label="Enviar">↑</button></div>`;
        document.body.append(fab, panel);
        const body = panel.querySelector('.ai-chat-body');
        const input = panel.querySelector('.ai-chat-input');
        const sendBtn = panel.querySelector('.ai-chat-send');
        function addBubble(role, text) {
            const b = el('div', 'ai-bubble ' + role, text);
            body.appendChild(b);
            body.scrollTop = body.scrollHeight;
            return b;
        }
        async function send() {
            const text = input.value.trim();
            if (!text) return;
            input.value = '';
            addBubble('user', text);
            const typing = addBubble('bot', 'Pensando…');
            try {
                const response = await fetch(API_CHAT, {
                    method: 'POST',
                    headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({contexto: text, restricciones: [], preferencias: []})
                });
                const data = await response.json();
                typing.remove();
                const razon = data?.recomendacion?.razon || 'Sin recomendaciones disponibles.';
                addBubble('bot', razon);
            } catch (e) {
                typing.remove();
                addBubble('bot', 'No pude consultar la IA en este momento.');
            }
        }
        fab.addEventListener('click', () => {
            const open = panel.style.display === 'flex';
            panel.style.display = open ? 'none' : 'flex';
            if (!open) input.focus();
        });
        panel.querySelector('.ai-chat-close').addEventListener('click', () => panel.style.display = 'none');
        sendBtn.addEventListener('click', send);
        input.addEventListener('keydown', e => { if (e.key === 'Enter') send(); });
        addBubble('bot', '¡Hola! Soy tu asistente de SmartResto. Cuéntame qué se te antoja.');
    }
    function init() {
        if (document.querySelector('.ai-fab')) return;
        injectStyles();
        buildChat();
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once: true});
    else init();
})();
