import {$,api,node,message} from './menu3d-common.js';
const select=$('m3d-restaurant');
if(select){
  const review=$('bulk-review'),rows=$('bulk-rows'),doc=$('bulk-document'),photo=$('bulk-photo');
  let busy=false, generation=0;
  const fields={nombre:'Nombre',precio:'Precio (S/)',categoria:'Categoría',descripcion:'Descripción',ingredientes:'Ingredientes',alergenos:'Alérgenos declarados',restricciones_dieteticas:'Restricciones dietéticas',etiquetas:'Etiquetas'};
  const lists=['ingredientes','alergenos','restricciones_dieteticas','etiquetas'];
  function state(value){busy=value;select.disabled=value;[...doc.elements,...photo.elements,...review.elements].forEach(e=>e.disabled=value||!select.value);if(!value)rows.querySelectorAll('article').forEach(card=>toggle(card));}
  function reset(){generation++;rows.replaceChildren();review.hidden=true;message('bulk-status','');}
  function links(){for(const [id,fmt] of [['bulk-excel','xlsx'],['bulk-word','docx']]){const a=$(id);if(select.value)a.href=`/ar/api/gestion/restaurantes/${select.value}/plantilla/${fmt}`;else a.removeAttribute('href');}reset();state(false);}
  function toggle(card){const include=card.querySelector('[data-include]');card.querySelectorAll('[data-field]').forEach(input=>input.disabled=!include.checked);}
  function render(dishes,categories){
    rows.replaceChildren();
    dishes.forEach((dish,index)=>{
      const card=node('article',undefined,'m3d-bulk-row'),label=node('label',undefined,'m3d-check'),include=node('input');include.type='checkbox';include.checked=true;include.dataset.include='';label.append(include,document.createTextNode(` Registrar plato ${index+1}`));card.append(label);
      const grid=node('div',undefined,'m3d-bulk-fields');
      for(const [key,title] of Object.entries(fields)){
        const label=node('label',title),input=node(key==='categoria'?'select':key==='descripcion'?'textarea':'input');input.dataset.field=key;input.value=Array.isArray(dish[key])?dish[key].join('; '):(dish[key]??'');
        if(key==='categoria'){
          const empty=node('option','Sin categoría');empty.value='';input.append(empty);
          for(const category of categories){const option=node('option',category);option.value=category;input.append(option);}
          const original=String(dish[key]||'');const canonical=categories.find(c=>c.toLocaleLowerCase()===original.toLocaleLowerCase());
          if(original&&!canonical){const unknown=node('option',original+' (elige una categoría válida)');unknown.value=original;unknown.disabled=true;unknown.selected=true;input.append(unknown);input.setCustomValidity('Selecciona una categoría válida o Sin categoría.');}
          else input.value=canonical||'';
          input.addEventListener('change',()=>input.setCustomValidity(''));
        }
        else if(key==='precio'){input.type='number';input.min='0';input.max='999999';input.step='0.01';input.required=true;input.placeholder='Confirma el precio';}
        else{input.maxLength=key==='nombre'?160:key==='categoria'?100:key==='descripcion'?2000:4100;input.required=key==='nombre';}
        label.append(input);grid.append(label);
      }
      card.append(grid);include.addEventListener('change',()=>toggle(card));rows.append(card);
    });review.hidden=false;
  }
  async function analyze(event){
    event.preventDefault();if(busy)return;
    const form=event.currentTarget, file=form.elements.archivo.files[0];
    if(!file||file.size>2*1024*1024){message('bulk-status','Selecciona un archivo de hasta 2 MB.',true);return;}
    const body=new FormData(form),rid=select.value,ticket=++generation;review.hidden=true;rows.replaceChildren();state(true);message('bulk-status','Leyendo tu carta…');
    try{const data=await api(`/ar/api/gestion/restaurantes/${rid}/importar/analizar`,{method:'POST',body});if(ticket!==generation)return;render(data.platos,data.categorias||[]);message('bulk-status',`${data.platos.length} platos encontrados. Revisa los datos antes de guardar.`);}
    catch(error){message('bulk-status',error.message,true);}finally{state(false);}
  }
  doc.addEventListener('submit',analyze);photo.addEventListener('submit',analyze);
  $('bulk-camera').addEventListener('change',event=>{if(event.target.files.length){photo.elements.archivo.files=event.target.files;message('bulk-status','Foto lista. Pulsa “Leer foto de la carta”.');}});
  review.addEventListener('submit',async event=>{
    event.preventDefault();if(busy)return;
    const platos=[...rows.children].filter(card=>card.querySelector('[data-include]').checked).map(card=>Object.fromEntries([...card.querySelectorAll('[data-field]')].map(input=>[input.dataset.field,lists.includes(input.dataset.field)?input.value.split(';').map(v=>v.trim()).filter(Boolean):input.value])));
    if(!platos.length){message('bulk-status','Selecciona al menos un plato.',true);return;}
    state(true);message('bulk-status','Registrando platos…');
    try{const data=await api(`/ar/api/gestion/restaurantes/${select.value}/importar/guardar`,{method:'POST',body:{confirmar:true,platos}});reset();doc.reset();photo.reset();message('bulk-status',`${data.total} platos registrados. Ya puedes añadir sus fotografías y modelos.`);select.dispatchEvent(new CustomEvent('menu-imported'));}
    catch(error){message('bulk-status',error.message,true);}finally{state(false);}
  });
  $('bulk-cancel').addEventListener('click',reset);select.addEventListener('change',links);links();
}
