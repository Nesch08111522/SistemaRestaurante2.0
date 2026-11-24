/* Radar SmartResto. */
(function () {
  'use strict';
  const status = document.getElementById('radarStatus');
  function message(text, error) { if (!status) return; status.hidden = false; status.classList.toggle('error', !!error); status.textContent = text; }
  async function api(path, data, method = 'POST') {
    const response = await fetch(path, { method, headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) });
    const result = await response.json();
    if (!response.ok || !result.success) throw new Error(result.error || 'La operación no se completó.');
    return result;
  }
  async function busy(button, action) {
    button.disabled = true; button.setAttribute('aria-busy','true');
    try { await action(); } catch(error) { message(error.message, true); }
    finally { button.disabled = false; button.removeAttribute('aria-busy'); }
  }
  const root = document.getElementById('radarApp');
  let decision = null;
  if (root) {
    const cards = Array.from(root.querySelectorAll('.radar-candidate'));
    const search = document.getElementById('radarSearch'), filter = document.getElementById('radarFilter');
    if (search && filter) {
      function applyFilters() {
        let count = 0;
        cards.forEach(card => {
          card.hidden = !!((filter.value && card.dataset.state !== filter.value) || !card.dataset.search.includes(search.value.toLowerCase()));
          if (!card.hidden) count++;
        });
        const noMatches = document.getElementById('radarNoMatches');
        if (noMatches) noMatches.hidden = count > 0 || !cards.length;
      }
      search.addEventListener('input', applyFilters);
      filter.addEventListener('change', applyFilters);
    }
    root.addEventListener('click', event => {
      const button = event.target.closest('button[data-action]'); if (!button) return;
      if (button.dataset.action === 'scan') busy(button, async () => {
        message('Consultando…');
        const result = await api('/admin/api/discovery/runs', {source:button.dataset.source});
        message(`Corrida completada.`);
        location.reload();
      });
    });
  }
})();
