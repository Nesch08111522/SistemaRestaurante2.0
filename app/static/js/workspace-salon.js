import {requestJSON, message} from './workspace-api.js';
const root = document.getElementById('salon');
if (root) {
  const endpoint = new URL(root.dataset.endpoint, location.href);
  const status = document.getElementById('salon-status');
  const container = document.getElementById('salon-tables');
  const form = document.getElementById('salon-create');
  const refresh = document.getElementById('salon-refresh');
  let busy = false;
  function node(tag, text, cls) {
    const element = document.createElement(tag);
    if (text) element.textContent = text;
    if (cls) element.className = cls;
    return element;
  }
  function url(suffix='') { return `${endpoint.pathname}${suffix}${endpoint.search}`; }
  async function load() {
    const result = await requestJSON(endpoint);
    container.replaceChildren();
    form.hidden = !result.can_manage;
    document.getElementById('salon-plan').hidden = result.can_manage;
    if (!result.mesas.length) container.append(node('p', 'Todavía no hay mesas registradas.'));
    for (const table of result.mesas) {
      const card = node('article', '', 'ws-card');
      card.append(node('h2', table.nombre), node('p', `${table.zona} · ${table.capacidad} personas`),
        node('p', `${table.estado}${table.estado === 'ocupada' ? ` · ${table.personas} comensales` : ''}`));
      const action = node('form');
      let people;
      if (table.estado === 'libre') {
        const label = node('label', 'Comensales ');
        people = node('input');
        Object.assign(people, {type:'number', min:'1', max:String(table.capacidad), value:'1', required:true});
        label.append(people); action.append(label);
      }
      const target = {libre:'ocupada', ocupada:'limpieza', limpieza:'libre'}[table.estado];
      const button = node('button', {libre:'Ocupar mesa', ocupada:'Finalizar atención', limpieza:'Marcar como limpia'}[table.estado], 'ws-button primary');
      button.type = 'submit'; action.append(button);
      action.addEventListener('submit', e => {
        e.preventDefault();
        if (!action.reportValidity()) return;
        run(() => requestJSON(url(`/${table.id_mesa}/estado`), {method:'POST', body:{expected_state:table.estado, target, personas:people ? Number(people.value) : 0}}));
      });
      card.append(action);
      if (result.can_manage && table.estado === 'libre') {
        const remove = node('button', 'Eliminar mesa', 'ws-button danger'); remove.type = 'button';
        remove.addEventListener('click', () => {
          if (confirm(`¿Eliminar la mesa ${table.nombre}?`)) run(() => requestJSON(url(`/${table.id_mesa}`), {method:'DELETE',body:{}}));
        });
        card.append(remove);
      }
      container.append(card);
    }
  }
  async function run(action) {
    if (busy) return;
    busy = true; root.querySelectorAll('button').forEach(b => b.disabled = true);
    message(status, 'Actualizando salón…');
    try { if (action) await action(); await load(); message(status, action ? 'Cambios guardados.' : 'Salón actualizado.'); }
    catch (error) { message(status, error.message, true); }
    finally { busy = false; root.querySelectorAll('button').forEach(b => b.disabled = false); }
  }
  form.addEventListener('submit', e => {
    e.preventDefault(); if (!form.reportValidity()) return;
    const data = Object.fromEntries(new FormData(form)); data.capacidad = Number(data.capacidad);
    run(() => requestJSON(endpoint, {method:'POST',body:data}));
  });
  refresh.addEventListener('click', () => run());
  run();
}
