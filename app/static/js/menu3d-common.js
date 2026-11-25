export const $ = id => document.getElementById(id);
export function node(tag, text, className) { const e=document.createElement(tag); if(text!==undefined)e.textContent=text; if(className)e.className=className; return e; }
export function button(text, action) { const b=node('button',text); b.type='button'; b.addEventListener('click',action); return b; }
export const price = value => value==null ? 'Precio no informado' : new Intl.NumberFormat('es-PE',{style:'currency',currency:'PEN'}).format(Number(value));
export function message(id,text,error=false){$(id).textContent=text;$(id).classList.toggle('m3d-error',error);}
export async function api(url,options={}) {
  const headers={Accept:'application/json',...options.headers};
  if(options.body && !(options.body instanceof FormData)){headers['Content-Type']='application/json';options.body=JSON.stringify(options.body);}
  if(options.method && options.method!=='GET') headers['X-CSRFToken']=document.querySelector('meta[name=csrf-token]')?.content||'';
  const response=await fetch(url,{credentials:'same-origin',...options,headers});
  let result;try{result=await response.json();}catch{throw Error('El servidor no pudo completar la solicitud. Inténtalo de nuevo.');}
  if(!response.ok)throw Error(result.error||'No se pudo completar la operación.');
  return result;
}
export function card(dish,actions) {
  const article=node('article',undefined,'m3d-card');
  if(dish.foto_url){const img=node('img');img.src=dish.foto_url;img.alt=dish.nombre;img.loading='lazy';img.width=600;img.height=400;img.addEventListener('error',()=>img.replaceWith(node('div','Fotografía no disponible','m3d-photo-empty')),{once:true});article.append(img);}
  else article.append(node('div','Fotografía pendiente','m3d-photo-empty'));
  const body=node('div',undefined,'m3d-card-body'),tags=node('div',undefined,'m3d-tags');
  [dish.categoria, dish.modelo_url?'Modelo 3D disponible':null,dish.esta_disponible?'Disponible':'No disponible',...(dish.etiquetas||[]),...(dish.restricciones_dieteticas||[])].filter(Boolean).forEach(t=>tags.append(node('span',t,'m3d-tag')));
  body.append(tags,node('h3',dish.nombre),node('p',dish.descripcion||''),node('p',price(dish.precio),'m3d-price'));
  const buttons=node('div',undefined,'m3d-actions');actions(buttons);body.append(buttons);article.append(body);return article;
}
export function createViewer(){
  const dialog=$('m3d-viewer'),stage=$('m3d-model'),status=$('m3d-viewer-status'),controls=$('m3d-controls');
  let viewer=null,revision=0,opener=null,timeout=null;
  function close(){revision++;clearTimeout(timeout);viewer?.remove();viewer=null;stage.replaceChildren();controls.hidden=true;opener?.focus();}
  $('m3d-close').addEventListener('click',()=>dialog.close());dialog.addEventListener('close',close);
  controls.addEventListener('click',async event=>{
    const control=event.target.closest('[data-control]');if(!control||!viewer)return;
    try{
      if(control.dataset.control==='reset'){viewer.cameraOrbit='0deg 75deg 105%';viewer.fieldOfView='30deg';viewer.jumpCameraToGoal();}
      if(control.dataset.control.startsWith('zoom-')){const fov=viewer.getFieldOfView();viewer.fieldOfView=`${Math.min(65,Math.max(12,fov+(control.dataset.control==='zoom-in'?-5:5)))}deg`;}
      if(control.dataset.control==='rotate'){const active=!viewer.hasAttribute('auto-rotate');viewer.toggleAttribute('auto-rotate',active);control.setAttribute('aria-pressed',String(active));}
      if(control.dataset.control==='fullscreen'){if(dialog.requestFullscreen)await dialog.requestFullscreen();else status.textContent='Este navegador no admite pantalla completa.';}
    }catch{status.textContent='El navegador no pudo activar este control.';}
  });
  return async function open(dish,loadModel=false){
    const ticket=++revision;if(!dialog.open)opener=document.activeElement;clearTimeout(timeout);viewer=null;stage.replaceChildren();controls.hidden=true;
    $('m3d-dish-title').textContent=dish.nombre;$('m3d-dish-price').textContent=price(dish.precio);
    const info=$('m3d-dish-info');info.replaceChildren(node('p',dish.descripcion||''),node('p',dish.esta_disponible?'Disponible':'No disponible'));
    if(dish.es_recomendado)info.append(node('span','Recomendado por el restaurante','m3d-tag'));
    for(const [key,label] of [['ingredientes','Ingredientes'],['alergenos','Alérgenos declarados'],['restricciones_dieteticas','Restricciones alimentarias'],['etiquetas','Características']]){
      if(dish[key]?.length){info.append(node('h3',label));const list=node('ul');dish[key].forEach(v=>list.append(node('li',v)));info.append(list);}
    }
    if(!dish.alergenos?.length)info.append(node('p','Alérgenos no informados. Consulta al restaurante; esto no significa que el plato esté libre de alérgenos.'));
    const nutrition=dish.info_nutricional||{};
    for(const [key,label] of [['calorias','Calorías'],['proteinas_g','Proteínas (g)'],['carbohidratos_g','Carbohidratos (g)'],['grasas_g','Grasas (g)']])if(nutrition[key]!=null)info.append(node('p',`${label}: ${nutrition[key]}`));
    if(dish.tiempo_preparacion_minutos!=null)info.append(node('p',`Preparación: ${dish.tiempo_preparacion_minutos} min`));
    if(dish.nivel_picante!=null)info.append(node('p',`Nivel de picante: ${dish.nivel_picante}`));
    function photo(){stage.replaceChildren();if(dish.foto_url){const img=node('img');img.src=dish.foto_url;img.alt=dish.nombre;stage.append(img);}else stage.append(node('p','Fotografía todavía no disponible.'));}
    photo();if(!dialog.open)dialog.showModal();
    status.textContent=dish.modelo_url?'Fotografía del plato.':'Modelo 3D todavía no disponible. Mostramos la fotografía original.';
    if(dish.modelo_url&&!loadModel){stage.append(button('Explorar en 3D',()=>open(dish,true)));return;}
    if(!loadModel||!dish.modelo_url)return;
    status.textContent='Cargando visor 3D…';
    try{
      const canvas=document.createElement('canvas');const gl=canvas.getContext('webgl2')||canvas.getContext('webgl');
      if(!gl)throw Error('WebGL');gl.getExtension('WEBGL_lose_context')?.loseContext();
      await import('/static/vendor/model-viewer/model-viewer-4.1.0.min.js');
      if(ticket!==revision||!dialog.open)return;
      viewer=document.createElement('model-viewer');viewer.src=dish.modelo_url;viewer.alt=`Modelo generado desde fotografías de ${dish.nombre}`;
      viewer.setAttribute('camera-controls','');viewer.setAttribute('touch-action','pan-y');viewer.setAttribute('shadow-intensity','.6');viewer.setAttribute('camera-orbit','0deg 75deg 105%');viewer.setAttribute('field-of-view','30deg');
      if(dish.foto_url)viewer.poster=dish.foto_url;
      viewer.addEventListener('load',()=>{if(ticket!==revision)return;clearTimeout(timeout);controls.hidden=false;status.textContent='Arrastra para girar 360°. Pellizca o usa + / − para acercarte. Con teclado, usa las flechas.';});
      viewer.addEventListener('error',()=>{if(ticket!==revision)return;clearTimeout(timeout);controls.hidden=true;photo();status.textContent='No se pudo cargar el modelo. Puedes consultar la fotografía.';});
      controls.querySelector('[data-control=rotate]').setAttribute('aria-pressed','false');
      controls.querySelector('[data-control=fullscreen]').hidden=!dialog.requestFullscreen;
      stage.replaceChildren(viewer);
      timeout=setTimeout(()=>{if(ticket===revision&&dialog.open&&controls.hidden){photo();status.textContent='La carga tardó demasiado. Cierra y vuelve a abrir el visor para reintentar.';}},45000);
    }catch{if(ticket===revision){photo();status.textContent='El visor no está disponible en este dispositivo. Mostramos la fotografía.';}}
  };
}
