(() => {
  'use strict';
  const page = document.querySelector('[data-recommendations]');
  if (!page) return;
  async function post(url, payload, keepalive = false) {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      keepalive,
    });
    const result = await response.json();
    if (!response.ok || !result.success) throw new Error(result.error || 'No se pudo guardar el cambio.');
    return result;
  }
  const cards = new Map();
  for (const card of page.querySelectorAll('[data-rec-card][data-token]')) {
    const entry = {
      card,
      list: card.closest('[data-rec-list]'),
      like: card.querySelector('[data-rec-like]'),
      dismiss: card.querySelector('[data-rec-dismiss]'),
      undo: card.querySelector('[data-rec-undo]'),
      body: card.querySelector('.rec-card-main'),
      dismissed: card.querySelector('[data-rec-dismissed]'),
    };
    const key = card.dataset.recKey;
    if (!cards.has(key)) cards.set(key, []);
    cards.get(key).push(entry);
    entry.like?.addEventListener('click', () => saveFeedback(entry, entry.like.getAttribute('aria-pressed') === 'true' ? 'undo' : 'like', entry.like));
    entry.dismiss?.addEventListener('click', () => saveFeedback(entry, 'dismiss', entry.dismiss));
    entry.undo?.addEventListener('click', () => saveFeedback(entry, 'undo', entry.undo));
  }
  async function saveFeedback(entry, action, button) {
    if (!entry.card || !page.dataset.interactionUrl) return;
    try {
      const result = await post(page.dataset.interactionUrl, { token: entry.card.dataset.token, action });
      const status = entry.list?.querySelector('[data-rec-feedback]');
      if (status) status.textContent = 'Guardado.';
    } catch (error) {
      const status = entry.list?.querySelector('[data-rec-feedback]');
      if (status) status.textContent = error.message;
    }
  }
})();
