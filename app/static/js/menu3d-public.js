import {$,api,button,card,node,message,createViewer} from './menu3d-common.js';
const root=$('menu3d');
if(root){
  const rid=root.dataset.restaurant,open=createViewer(),form=$('m3d-filters');let category='',page=1,controller;
  const actions=dish=>container=>{if(dish.modelo_url)container.append(button('Explorar en 3D',()=>open(dish,true)));container.append(button('Ver detalles',()=>open(dish)));};
  async function load(){
    controller?.abort();controller=new AbortController();const signal=controller.signal;
    $('m3d-grid').setAttribute('aria-busy','true');message('m3d-message','Cargando platos…');
    const params=new URLSearchParams(new FormData(form));params.set('page',page);if(category)params.set('categoria',category);
    try{const data=await api(`/ar/api/restaurantes/${rid}/menu?${params}`,{signal});
      $('m3d-grid').replaceChildren(...data.platos.map(d=>card(d,actions(d))));
      if(!data.platos.length)$('m3d-grid').append(node('p','No hay platos con estos filtros. Prueba otra categoría o limpia la búsqueda.','m3d-empty'));
      $('m3d-prev').disabled=page===1;$('m3d-next').disabled=!data.hay_mas;$('m3d-page').textContent=`Página ${page}`;
      message('m3d-message',`${data.platos.length} platos en esta página.`);
    }catch(e){if(e.name!=='AbortError'){message('m3d-message',e.message,true);$('m3d-grid').replaceChildren(button('Volver a cargar',load));}}
    finally{if(!signal.aborted)$('m3d-grid').setAttribute('aria-busy','false');}
  }
  form.addEventListener('submit',e=>{e.preventDefault();page=1;load();});
  let debounce;form.elements.q.addEventListener('input',()=>{clearTimeout(debounce);debounce=setTimeout(()=>{page=1;load();},300);});
  form.addEventListener('reset',()=>{category='';page=1;setTimeout(()=>{setCategoryButtons();load();},0);});
  function setCategoryButtons(){for(const b of $('m3d-categories').children)b.setAttribute('aria-pressed',String(b.dataset.category===category));}
  $('m3d-prev').addEventListener('click',()=>{page--;load();});$('m3d-next').addEventListener('click',()=>{page++;load();});
  $('m3d-share').addEventListener('click',async()=>{try{if(navigator.share)await navigator.share({title:document.title,url:location.href});else{await navigator.clipboard.writeText(location.href);message('m3d-message','Enlace del menú copiado.');}}catch(e){if(e.name!=='AbortError')message('m3d-message','Puedes copiar el enlace desde la barra de direcciones.');}});
  async function initialize(){
    try{const data=await api(`/ar/api/restaurantes/${rid}/categorias`);for(const name of ['',...data.categorias]){const b=button(name||'Todos los platos',()=>{category=name;page=1;setCategoryButtons();load();});b.dataset.category=name;$('m3d-categories').append(b);}setCategoryButtons();}catch(e){message('m3d-message',e.message,true);}
    await load();
    try{const data=await api(`/ar/api/restaurantes/${rid}/menu?recomendado=1`);$('m3d-recommended').hidden=!data.platos.length;$('m3d-recommended-grid').replaceChildren(...data.platos.slice(0,3).map(d=>card(d,actions(d))));}catch{/* Main catalog reports service errors. */}
  }
  initialize();
}
