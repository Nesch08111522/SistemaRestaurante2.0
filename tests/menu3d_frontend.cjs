const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.attributes={};this.listeners={};this.textContent='';this.hidden=false;this.open=false;this.classList={toggle(){}};}
  append(...nodes){this.children.push(...nodes);}
  replaceChildren(...nodes){this.children=nodes;}
  setAttribute(k,v){this.attributes[k]=v;}
  getAttribute(k){return this.attributes[k];}
  addEventListener(name,fn){this.listeners[name]=fn;}
  showModal(){this.open=true;}
  close(){this.open=false;this.listeners.close?.();}
  focus(){this.focused=true;}
  remove(){}
}
function setup(fetch){
  const ids=new Map();const document={activeElement:new Element('button'),
    getElementById(id){if(!ids.has(id))ids.set(id,new Element('div'));return ids.get(id);},
    createElement:tag=>new Element(tag),querySelector:()=>({content:'csrf-test'})};
  const context=vm.createContext({document,fetch,Intl,FormData:class {},setTimeout,clearTimeout,console});
  let source=fs.readFileSync('app/static/js/menu3d-common.js','utf8').replace(/export /g,'');
  source+='\nglobalThis.helpers={api,card,button,createViewer};';vm.runInContext(source,context);
  return {document,ids,...context.helpers};
}
test('mutations send CSRF and use same-origin credentials',async()=>{
  let sent;const h=setup(async(url,options)=>{sent=options;return {ok:true,json:async()=>({success:true})};});
  await h.api('/ar/api/gestion/platos/1/publicacion',{method:'POST',body:{publicado:false}});
  assert.equal(sent.headers['X-CSRFToken'],'csrf-test');assert.equal(sent.credentials,'same-origin');assert.equal(sent.body,'{"publicado":false}');
});
test('HTTP errors remain visible and are not reported as success',async()=>{
  const h=setup(async()=>({ok:false,json:async()=>({error:'No autorizado'})}));
  await assert.rejects(h.api('/ar/api/gestion/recursos/1'),/No autorizado/);
});
test('cards render text safely and never preload GLB',()=>{
  const h=setup();const card=h.card({nombre:'<script>bad</script>',precio:12,descripcion:'<img onerror=x>',modelo_url:'/private.glb'},()=>{});
  const body=card.children[1];assert.equal(body.children[1].textContent,'<script>bad</script>');
  assert.equal(JSON.stringify(card).includes('private.glb'),false);
});
test('missing model shows explicit fallback and dialog closes with restored focus',async()=>{
  const h=setup();const opener=h.document.activeElement;const open=h.createViewer();
  await open({nombre:'QA',precio:10,modelo_url:null});
  assert.equal(h.ids.get('m3d-viewer').open,true);
  assert.match(h.ids.get('m3d-viewer-status').textContent,/todavía no disponible/);
  assert.equal(h.ids.get('m3d-controls').hidden,true);
  h.ids.get('m3d-viewer').close();assert.equal(opener.focused,true);
});
test('details do not import model-viewer until explicitly requested',async()=>{
  const h=setup();const open=h.createViewer();
  await open({nombre:'QA',precio:10,modelo_url:'/private.glb'},false);
  assert.equal(h.ids.get('m3d-viewer-status').textContent,'Fotografía del plato.');
  assert.equal(h.ids.get('m3d-model').children.at(-1).textContent,'Explorar en 3D');
});
test('WebGL unavailable falls back to photograph',async()=>{
  const h=setup();const create=h.document.createElement;h.document.createElement=tag=>tag==='canvas'?{getContext:()=>null}:create(tag);
  await h.createViewer()({nombre:'QA',precio:10,modelo_url:'/qa.glb',foto_url:'/photo'},true);
  assert.match(h.ids.get('m3d-viewer-status').textContent,/no está disponible en este dispositivo/);
  assert.equal(h.ids.get('m3d-model').children[0].src,'/photo');
});
