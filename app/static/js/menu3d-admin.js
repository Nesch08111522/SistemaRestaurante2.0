import {$,api,button,card,node,message,createViewer} from './menu3d-common.js';
const root=$('menu3d-admin');
if(root){
  const select=$('m3d-restaurant'),open=createViewer(),form=$('m3d-dish-form'),studio=$('m3d-studio');
  let page=1,editing=null,currentDish=null,pollTimer=null,canGenerate=false,confirmation=null,revision=0,previewURLs=[];
  const names={pendiente:'Pendiente',en_cola:'En cola',procesando:'Procesando',completado:'Completado',fallido:'Fallido',rechazado:'Rechazado'};
  root.querySelectorAll('[data-close]').forEach(b=>b.addEventListener('click',()=>$(b.dataset.close).close()));
  const clearPreviews=()=>{previewURLs.forEach(URL.revokeObjectURL);previewURLs=[];$('m3d-photo-preview').replaceChildren();};
  studio.addEventListener('close',()=>{clearTimeout(pollTimer);revision++;clearPreviews();});
  function editor(dish=null){editing=dish;form.reset();for(const name of ['nombre','precio','categoria','descripcion','ingredientes','restricciones_dieteticas','etiquetas','alergenos'])form.elements[name].value=Array.isArray(dish?.[name])?dish[name].join('\n'):(dish?.[name]??'');form.elements.esta_disponible.checked=dish?!!dish.esta_disponible:true;form.elements.es_recomendado.checked=!!dish?.es_recomendado;message('m3d-editor-message','');$('m3d-editor').showModal();}
  $('m3d-new').addEventListener('click',()=>editor());
  async function load(){
    if(!select.value)return;
    const ticket=++revision;message('m3d-message','Cargando carta…');
    try{const data=await api(`/ar/api/gestion/restaurantes/${select.value}?page=${page}`);if(ticket!==revision)return;
      canGenerate=data.puede_generar;const labels={total:'Total de platos',publicados:'Publicados',generados:'Con modelo generado',procesando:'En procesamiento',errores:'Con errores',sin_modelo:'Sin modelo'};
      $('m3d-stats').replaceChildren(...Object.entries(labels).map(([key,label])=>{const e=node('div',undefined,'m3d-stat');e.append(node('strong',data.resumen[key]),node('span',label));return e;}));
      $('m3d-admin-grid').replaceChildren(...data.platos.map(d=>card(d,container=>{
        container.append(node('span',d.publicado?'Publicado':'Borrador','m3d-tag'),button('Editar',()=>editor(d)),button('Fotos y modelos',()=>startStudio(d)),button(d.publicado?'Despublicar':'Publicar plato',async e=>{
          e.currentTarget.disabled=true;try{await api(`/ar/api/gestion/platos/${d.id_plato}/publicacion`,{method:'POST',body:{publicado:!d.publicado}});await load();message('m3d-message',d.publicado?'Plato retirado del menú público.':'Plato publicado. Solo se mostrará un modelo si ha sido aprobado.');}catch(err){message('m3d-message',err.message,true);e.target.disabled=false;}
        }),button('Asignar porciones',async event=>{
          event.currentTarget.disabled=true;
          try{
            const current=await api(`/ar/api/gestion/platos/${d.id_plato}/stock`);
            const value=window.prompt(`Porciones disponibles para ${d.nombre}:`,String(current.stock.disponibles));
            if(value===null)return;
            if(!/^\d+$/.test(value.trim()))throw Error('Ingresa un número entero de porciones.');
            await api(`/ar/api/gestion/platos/${d.id_plato}/stock`,{method:'PUT',body:{cantidad:Number(value),version:current.stock.version}});
            message('m3d-message','Porciones actualizadas.');
          }catch(err){message('m3d-message',err.message,true);}finally{event.currentTarget.disabled=false;}
        }));if(d.modelo_url)container.append(button('Explorar en 3D',()=>open(d,true)));
      })));
      if(!data.platos.length)$('m3d-admin-grid').append(node('p','Registra tu primer plato para empezar.','m3d-empty'));
      $('m3d-prev').disabled=page===1;$('m3d-next').disabled=!data.hay_mas;$('m3d-page').textContent=`Página ${page}`;
      $('m3d-public-link').href=`/ar/restaurantes/${select.value}`;$('m3d-public-link').hidden=false;message('m3d-message','');
    }catch(e){if(ticket===revision)message('m3d-message',e.message,true);}
  }
  select.addEventListener('change',()=>{page=1;load();});$('m3d-prev').addEventListener('click',()=>{page--;load();});$('m3d-next').addEventListener('click',()=>{page++;load();});
  form.addEventListener('submit',async e=>{
    e.preventDefault();const submit=form.querySelector('[type=submit]');submit.disabled=true;const payload={};
    for(const name of ['nombre','precio','categoria','descripcion'])payload[name]=form.elements[name].value;
    for(const name of ['ingredientes','restricciones_dieteticas','etiquetas','alergenos'])payload[name]=form.elements[name].value.split('\n').map(s=>s.trim()).filter(Boolean);
    for(const name of ['esta_disponible','es_recomendado'])payload[name]=form.elements[name].checked;
    try{await api(editing?`/ar/api/gestion/platos/${editing.id_plato}`:`/ar/api/gestion/restaurantes/${select.value}/platos`,{method:editing?'PUT':'POST',body:payload});$('m3d-editor').close();await load();message('m3d-message','Plato guardado.');}catch(err){message('m3d-editor-message',err.message,true);}finally{submit.disabled=false;}
  });
  async function startStudio(dish){currentDish=dish;revision++;$('m3d-studio-title').textContent=dish.nombre;$('m3d-photo-form').reset();clearPreviews();$('m3d-resources').replaceChildren();message('m3d-studio-message','');studio.showModal();await resources();}
  async function resources(){
    clearTimeout(pollTimer);const pid=currentDish?.id_plato;if(!pid||!studio.open)return;
    try{const data=await api(`/ar/api/gestion/platos/${pid}/recursos`);if(!studio.open||pid!==currentDish?.id_plato)return;
      $('m3d-resources').replaceChildren(...data.recursos.map(resource=>{
        const e=node('article',undefined,'m3d-resource');e.append(node('h3',`Versión ${resource.version} · ${names[resource.estado]||resource.estado}${resource.aprobado?' · Aprobado':''}`));
        const progress=node('progress');progress.max=100;progress.value=resource.progreso;progress.setAttribute('aria-label',`Progreso de versión ${resource.version}`);e.append(progress,node('p',`${resource.progreso}%`));
        if(resource.error_mensaje)e.append(node('p',resource.error_mensaje,'m3d-error'));
        const actions=node('div',undefined,'m3d-actions');e.append(actions);
        actions.append(button('Ver fotografía',()=>open({...currentDish,foto_url:resource.foto_url,modelo_url:null})));
        if(resource.estado==='pendiente' || (resource.estado==='fallido'&&['servicio_temporal','tiempo_agotado'].includes(resource.error_codigo))){const b=button(resource.estado==='pendiente'?'Generar modelo 3D':'Reanudar tarea',()=>confirm(resource));b.disabled=!canGenerate;actions.append(b);}
        if(resource.modelo_url)actions.append(button('Revisar en 3D',()=>open({...currentDish,foto_url:resource.foto_url,modelo_url:resource.modelo_url},true)));
        if(['completado','rechazado','fallido'].includes(resource.estado)&&resource.error_codigo!=='envio_incierto'&&canGenerate)actions.append(button('Nueva versión con estas fotos',async event=>{
          event.currentTarget.disabled=true;
          try{const data=await api(`/ar/api/gestion/recursos/${resource.id_recurso}/regenerar`,{method:'POST',body:{}});await resources();confirm(data.recurso);}catch(error){message('m3d-studio-message',error.message,true);event.target.disabled=false;}
        }));
        if(resource.estado==='completado'){
          if(!resource.aprobado)actions.append(button('Aprobar para el menú',()=>review(resource,true)));
          actions.append(button('Rechazar modelo',()=>review(resource,false)));
        }
        return e;
      }));
      if(!data.recursos.length)$('m3d-resources').append(node('p','Sube fotografías para crear la primera versión.'));
      if(!canGenerate)message('m3d-studio-message','La generación requiere el permiso de IA y una suscripción compatible. Puedes gestionar fotos y revisar modelos existentes.');
      if(data.recursos.some(r=>['en_cola','procesando'].includes(r.estado)))pollTimer=setTimeout(()=>{if(!document.hidden)resources();else pollTimer=setTimeout(resources,10000);},10000);
    }catch(e){message('m3d-studio-message',e.message,true);if(studio.open)pollTimer=setTimeout(resources,30000);}
  }
  async function review(resource,approved){try{await api(`/ar/api/gestion/recursos/${resource.id_recurso}/revision`,{method:'POST',body:{aprobado:approved}});message('m3d-studio-message',approved?'Modelo aprobado. Será visible si el plato está publicado.':'Modelo rechazado; no se mostrará en el menú.');await resources();}catch(e){message('m3d-studio-message',e.message,true);}}
  function confirm(resource){confirmation={resource,key:crypto.randomUUID()};message('m3d-confirm-message','');$('m3d-confirm').showModal();}
  $('m3d-confirm-cancel').addEventListener('click',()=>$('m3d-confirm').close());
  $('m3d-confirm-yes').addEventListener('click',async e=>{
    e.currentTarget.disabled=true;
    try{await api(`/ar/api/gestion/recursos/${confirmation.resource.id_recurso}/generar`,{method:'POST',body:{confirmar_costo:true,clave_idempotencia:confirmation.key}});$('m3d-confirm').close();message('m3d-studio-message','Solicitud guardada. El trabajador procesará el modelo; puedes cerrar esta ventana.');await resources();}catch(err){message('m3d-confirm-message',err.message,true);}finally{$('m3d-confirm-yes').disabled=false;}
  });
  const photoForm=$('m3d-photo-form');photoForm.elements.fotos.addEventListener('change',()=>{
    clearPreviews();const files=[...photoForm.elements.fotos.files];
    if(files.length>4||files.some(f=>f.size>2*1024*1024||!['image/jpeg','image/png','image/webp'].includes(f.type))){message('m3d-studio-message','Selecciona hasta cuatro imágenes JPEG, PNG o WebP de máximo 2 MB cada una.',true);photoForm.reset();return;}
    for(const file of files){const url=URL.createObjectURL(file);previewURLs.push(url);const img=node('img');img.src=url;img.alt='Vista previa de fotografía seleccionada';$('m3d-photo-preview').append(img);}message('m3d-studio-message','Revisa que todas las fotos correspondan al mismo plato.');
  });
  photoForm.addEventListener('submit',async e=>{
    e.preventDefault();const b=photoForm.querySelector('[type=submit]');b.disabled=true;
    try{await api(`/ar/api/gestion/platos/${currentDish.id_plato}/fotografias`,{method:'POST',body:new FormData(photoForm)});photoForm.reset();clearPreviews();message('m3d-studio-message','Fotografías guardadas. La generación requiere tu confirmación de costo.');await resources();}catch(err){message('m3d-studio-message',err.message,true);}finally{b.disabled=false;}
  });
  select.addEventListener('menu-imported',()=>{page=1;load();});
  studio.addEventListener('close',load);load();
}
