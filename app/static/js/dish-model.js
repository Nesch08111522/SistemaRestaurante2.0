(() => {
 const button=document.getElementById('load-dish-model');if(!button)return;
 const status=document.getElementById('model-status'),controls=document.getElementById('immersive-controls');let viewer;
 async function track(event){try{await fetch(button.dataset.event,{method:'POST',body:new URLSearchParams({event})});}catch{}}
 button.addEventListener('click',async()=>{
  button.disabled=true;status.textContent='Cargando visor…';
  try{
   const [metadataResponse]=await Promise.all([fetch(button.dataset.metadata,{headers:{Accept:'application/json'}}),import('/static/vendor/model-viewer/model-viewer-4.1.0.min.js')]);
   if(!metadataResponse.ok)throw Error('metadata');const meta=await metadataResponse.json();
   viewer=document.createElement('model-viewer');
   viewer.setAttribute('src',button.dataset.src);
   viewer.setAttribute('camera-controls','');
   viewer.setAttribute('touch-action','pan-y');
   viewer.setAttribute('loading','lazy');
   viewer.setAttribute('shadow-intensity','.7');
   viewer.setAttribute('alt','Modelo del plato');
   viewer.style.cssText='width:100%;height:400px;max-height:65vh;touch-action:pan-y';
   viewer.addEventListener('load',()=>{
    if (controls) controls.hidden=false;
    status.textContent='Arrastra para girar 360°.';
    track('model');
   });
   viewer.addEventListener('error',()=>{status.textContent='El modelo no pudo cargarse.';button.disabled=false;if(controls)controls.hidden=true;});
   document.getElementById('dish-model').replaceChildren(viewer);
  }catch{status.textContent='No se pudo cargar el visor.';button.disabled=false;}
 });
 controls?.querySelectorAll('[data-camera]').forEach(b=>b.addEventListener('click',()=>viewer?.setAttribute('camera-orbit',b.dataset.camera)));
 document.getElementById('model-rotate')?.addEventListener('click',e=>{const active=e.currentTarget.getAttribute('aria-pressed')!=='true';e.currentTarget.setAttribute('aria-pressed',String(active));viewer?.toggleAttribute('auto-rotate',active);});
})();
