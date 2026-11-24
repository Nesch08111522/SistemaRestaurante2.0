/* Copilot interactivo (base funcional). */
(() => {
  const form = document.getElementById('copilot-question');
  if (!form) return;
  const status = document.getElementById('copilot-status');
  const conversation = document.getElementById('copilot-conversation');
  const input = document.getElementById('copilot-message');
  const show = text => { if (status) status.textContent = text; };
  let busy = false;
  function turn(role, text) {
    if (!conversation) return;
    const article = document.createElement('article');
    article.className = 'copilot-turn ' + role;
    const label = document.createElement('strong'); label.textContent = role === 'user' ? 'Tú' : 'SmartResto Copilot';
    const p = document.createElement('p'); p.textContent = text;
    article.append(label, p);
    conversation.hidden = false;
    conversation.append(article);
    conversation.scrollTop = conversation.scrollHeight;
  }
  form.addEventListener('submit', async e => {
    e.preventDefault(); if (busy) return;
    const message = input.value.trim(); if (!message) return;
    busy = true; show('Consultando…');
    turn('user', message);
    try {
      const response = await fetch('/descubrir/api/recommend', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({contexto: message, restricciones: [], preferencias: []})
      });
      const result = await response.json();
      const reply = result?.recomendacion?.razon || 'Sin respuesta.';
      turn('assistant', reply);
      input.value = '';
      show('Listo.');
    } catch (err) {
      show('Error al consultar.');
    } finally {
      busy = false;
    }
  });
})();
