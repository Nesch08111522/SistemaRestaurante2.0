import {requestJSON, message} from './workspace-api.js';
const status = document.getElementById('favorite-status');
let busy = false;
async function save(url, favorite, button) {
  if (busy) return;
  busy = true; button.disabled = true; message(status, 'Actualizando favoritos…');
  try { await requestJSON(url, {method:'PUT', body:{favorite}}); location.reload(); }
  catch (error) { message(status, error.message, true); }
  finally { busy = false; button.disabled = false; }
}
document.getElementById('favorite-add')?.addEventListener('submit', e => {
  e.preventDefault(); const select = document.getElementById('favorite-restaurant');
  if (e.currentTarget.reportValidity()) save(select.value, true, e.currentTarget.querySelector('button'));
});
document.querySelectorAll('[data-remove-favorite]').forEach(button => button.addEventListener('click', () => save(button.dataset.removeFavorite, false, button)));
