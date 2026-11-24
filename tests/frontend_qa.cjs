const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const read = name => fs.readFileSync('app/static/js/' + name, 'utf8');

test('database rows become valid escaped cards with working business links', () => {
  const context = vm.createContext({window: {}});
  for (const file of ['forest/processor.js', 'forest/logic-rules.js', 'forest/ui.js']) vm.runInContext(read(file), context);
  const r = context.window.ForestProcessor.restaurant({id_restaurante:7,nombre:'<script>bad</script>',distrito:'Trujillo',precio_promedio:25});
  const html = context.window.ForestUI.renderRestaurantCard(r);
  assert.ok(html.includes('/negocio/7'));
  assert.ok(html.includes('&lt;script&gt;'));
  assert.ok(!html.includes('<script>'));
  assert.equal(r.avg_price, 25);
});

test('home controller tolerates absent optional map, filters and modal', () => {
  const listeners = [];
  const element = {addEventListener(){}};
  const context = vm.createContext({window: {}, document: {
    addEventListener(event, fn) {listeners.push(fn)},
    body: {classList: {contains: () => true}},
    getElementById: id => id === 'search-form' ? element : null,
    querySelector: () => null,
  }, matchMedia: () => ({addEventListener(){}})});
  vm.runInContext(read('forest/controller.js'), context);
  assert.doesNotThrow(() => listeners[0]());
});

test('search uses GET and renders Spanish API response', async () => {
  let requested;
  const context = vm.createContext({window: {}, document: {
    addEventListener(){}, getElementById: () => null, querySelector: () => null
  }, URLSearchParams, AbortController, FormData: class {get(){return 'ceviche'}},
  fetch: async (url, options) => {requested={url,options}; return {ok:true,json:async()=>({restaurantes:[{id_restaurante:1}]})}}, console});
  vm.runInContext(read('search.js') + ';globalThis.Search = RealTimeSearch;', context);
  const search = new context.Search();
  let results;
  search.updateResults = value => {results=value};
  search.updateMapMarkers = () => {};
  await search.performSearch();
  assert.ok(requested.url.includes('/descubrir/api/restaurants?q=ceviche'));
  assert.equal(requested.options.method, undefined);
  assert.equal(results[0].id_restaurante, 1);
});
