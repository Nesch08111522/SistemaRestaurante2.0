const panel=document.getElementById('document-import');
const business=document.getElementById('business-registration');
if(panel && business) {
  const upload=document.getElementById('document-upload');
  const file=document.getElementById('business-document');
  const status=document.getElementById('document-status');
  const preview=document.getElementById('document-preview');
  const proposals=document.getElementById('document-proposals');
  const warnings=document.getElementById('document-warnings');
  const submit=upload.querySelector('button');
  let busy=false, rows=[];
  const announce=(text,error=false)=>{status.hidden=!text;status.textContent=text;status.classList.toggle('error',error);};
  function element(tag,text,cls) { const el=document.createElement(tag);el.textContent=text||'';if(cls)el.className=cls;return el; }
  function clear() { rows=[];proposals.replaceChildren();warnings.replaceChildren();preview.hidden=true; }
  file.addEventListener('change',()=>{clear();announce('');});
  upload.addEventListener('submit',async event=>{
    event.preventDefault();if(busy || !upload.reportValidity())return;
    const selected=file.files[0];
    if(!/\.(xlsx|docx)$/i.test(selected.name) || selected.size>1024*1024){announce('Usa un .xlsx o .docx de hasta 1 MB.',true);return;}
    clear();busy=true;submit.disabled=true;file.disabled=true;announce('Leyendo el documento y buscando datos del negocio…');
    try {
      const body=new FormData();body.append('file',selected);
      const response=await fetch(panel.dataset.endpoint,{method:'POST',credentials:'same-origin',headers:{Accept:'application/json','X-CSRFToken':document.querySelector('meta[name="csrf-token"]').content},body});
      const data=(response.headers.get('Content-Type')||'').includes('application/json') ? await response.json():null;
      if(response.redirected || response.status===401)throw new Error('Tu sesión expiró. Inicia sesión nuevamente.');
      if(!response.ok || !data?.success)throw new Error(data?.error || (response.status===413?'El archivo supera el tamaño permitido.':'No se pudo analizar el archivo. Inténtalo nuevamente.'));
      for(const proposal of data.proposals) {
        const target=business.elements.namedItem(proposal.field);
        if(!target)continue;
        const label=element('label','','ws-card');
        const check=document.createElement('input');check.type='checkbox';check.checked=!String(target.value||'').trim();
        const title=element('strong',` ${proposal.label}`);
        const value=element('p',proposal.display);
        const evidence=element('p',`Referencia: ${proposal.evidence}`,'muted');
        label.append(check,title,value,evidence);
        if(target.value)label.append(element('small',`Valor actual: ${target.value}. Selecciona para reemplazarlo.`,'muted'));
        if(target.disabled) {check.checked=false;check.disabled=true;label.append(element('small','La privacidad de ubicación mantiene este campo desactivado.','muted'));}
        proposals.append(label);rows.push({proposal,check,target,original:target.value});
      }
      for(const warning of data.warnings)warnings.append(element('li',warning));
      preview.hidden=rows.length===0;
      announce(rows.length?`${rows.length} campos detectados. Revisa las referencias antes de aplicarlos.`:'No hay sugerencias aplicables a este formulario.');
    } catch(error) {announce(error.message||'No se pudo conectar con el servidor.',true);}
    finally {busy=false;submit.disabled=false;file.disabled=false;}
  });
  document.getElementById('document-discard').addEventListener('click',()=>{clear();announce('Análisis descartado. El formulario no cambió.');});
  document.getElementById('document-apply').addEventListener('click',()=>{
    let applied=0,skipped=0;
    for(const {proposal,check,target,original} of rows) {
      if(!check.checked || check.disabled)continue;
      if(target.disabled || target.value!==original){skipped++;continue;}
      target.value=proposal.value;
      // RadioNodeList has no dispatchEvent; notify the checked radio instead.
      const node=typeof target.dispatchEvent==='function'?target:[...target].find(n=>n.checked);
      node?.dispatchEvent(new Event('input',{bubbles:true}));node?.dispatchEvent(new Event('change',{bubbles:true}));applied++;
    }
    if(applied){clear();announce(`${applied} campos aplicados. ${skipped?'Se omitieron campos que cambiaste después del análisis. ':''}Revisa el formulario y pulsa Guardar para confirmar.`);}
    else announce(skipped?'Los campos seleccionados cambiaron desde el análisis; vuelve a analizar para no sobrescribirlos.':'Selecciona al menos un campo para aplicar.');
  });
}
