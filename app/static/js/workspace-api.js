/** Private UI transport. Preserves HTTP errors; never automatically retries mutations. */
export async function requestJSON(url, {method = 'GET', body, signal} = {}) {
  const target = new URL(url, location.href);
  if (target.origin !== location.origin) throw new Error('La solicitud debe permanecer en SmartResto.');
  const headers = {Accept: 'application/json'};
  if (method !== 'GET') headers['X-CSRFToken'] = document.querySelector('meta[name="csrf-token"]')?.content || '';
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  const response = await fetch(target, {method, headers, credentials:'same-origin', signal, body:body === undefined ? undefined : JSON.stringify(body)});
  const json = (response.headers.get('Content-Type') || '').includes('application/json');
  const data = json ? await response.json() : null;
  if (response.redirected || response.status === 401) throw new Error('Tu sesión expiró. Inicia sesión nuevamente.');
  if (!response.ok || !json) throw new Error(data?.error || (response.status === 403 ? 'No tienes permiso para esta acción.' : 'No se pudo completar la solicitud. Inténtalo nuevamente.'));
  return data;
}
export function message(node, text, error = false) {
  if (!node) return;
  node.textContent = text;
  node.hidden = !text;
  node.classList.toggle('error', error);
}
