import {requestJSON, message} from './workspace-api.js';
const status = document.getElementById('order-status');
document.querySelectorAll('[data-order-action]').forEach(button => button.addEventListener('click', async () => {
  if (button.disabled) return;
  button.disabled = true; message(status, 'Actualizando pedido…');
  try {
    const result = await requestJSON(button.dataset.endpoint, {method:'POST', body:{target:button.dataset.target, expected_state:button.dataset.expected}});
    message(status, result.message); setTimeout(() => location.reload(), 250);
  } catch (error) { message(status, error.message, true); button.disabled = false; }
}));
