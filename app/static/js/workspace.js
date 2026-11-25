import {requestJSON, message} from './workspace-api.js';
const sidebar = document.getElementById('workspace-navigation');
const toggle = document.querySelector('.ws-menu-toggle');
const backdrop = document.querySelector('.ws-backdrop');
function menu(open) {
  sidebar?.classList.toggle('is-open', open);
  document.body.classList.toggle('ws-menu-open', open);
  toggle?.setAttribute('aria-expanded', String(open));
  if (backdrop) backdrop.hidden = !open;
  if (open) sidebar?.querySelector('a')?.focus();
  else toggle?.focus();
}
toggle?.addEventListener('click', () => menu(toggle.getAttribute('aria-expanded') !== 'true'));
backdrop?.addEventListener('click', () => menu(false));
document.addEventListener('keydown', e => {
  if (!sidebar?.classList.contains('is-open')) return;
  if (e.key === 'Escape') menu(false);
  if (e.key === 'Tab') {
    const nodes = [...sidebar.querySelectorAll('a[href],button:not([disabled])')];
    if (e.shiftKey && document.activeElement === nodes[0]) { e.preventDefault(); nodes.at(-1)?.focus(); }
    else if (!e.shiftKey && document.activeElement === nodes.at(-1)) { e.preventDefault(); nodes[0]?.focus(); }
  }
});
matchMedia('(min-width:1101px)').addEventListener('change', e => { if (e.matches && sidebar?.classList.contains('is-open')) menu(false); });
// Forms opt into this handler explicitly. A mutation is submitted once, with an actionable result.
document.querySelectorAll('form[data-workspace-form]').forEach(form => {
  let busy = false;
  form.addEventListener('submit', async event => {
    event.preventDefault(); if (busy || !form.reportValidity()) return;
    const data = Object.fromEntries(new FormData(form));
    delete data.csrf_token;
    if (form.querySelector('[name="restriction-choice"]')) {
      data.restrictions = [...form.querySelectorAll('[name="restriction-choice"]:checked')].map(node => node.value);
      delete data['restriction-choice'];
    }
    for (const node of form.querySelectorAll('[data-list]')) data[node.name] = node.value.split(/\r?\n/).map(x=>x.trim()).filter(Boolean);
    for (const node of form.querySelectorAll('[data-integer]')) data[node.name] = Number(node.value);
    busy = true;
    const button = form.querySelector('[type="submit"]'); if (button) button.disabled = true;
    const status = form.querySelector('[role="status"]'); message(status, 'Guardando…');
    try {
      const result = await requestJSON(form.action, {method:form.dataset.method || 'POST', body:data});
      if (form.dataset.reload === 'true') location.reload();
      else message(status, result.message || 'Cambios guardados.');
    } catch (error) { message(status, error.message || 'No se pudo conectar. Revisa tu conexión e inténtalo nuevamente.', true); }
    finally { busy = false; if (button) button.disabled = false; }
  });
});
