(() => {
  const $ = (s, r=document) => r.querySelector(s);
  const $$ = (s, r=document) => [...r.querySelectorAll(s)];
  const toast = (message) => {
    let node = $('#toast');
    if (!node) { node=document.createElement('div'); node.id='toast'; node.className='toast'; document.body.appendChild(node); }
    node.textContent=message; node.classList.add('show'); clearTimeout(window.__toastTimer); window.__toastTimer=setTimeout(()=>node.classList.remove('show'),3000);
  };
  const openModal = (title, body) => {
    const host=$('#modal-backdrop'); if(!host)return;
    host.innerHTML=`<div class="modal" role="dialog" aria-modal="true"><button class="modal-close" aria-label="Cerrar">✕</button><h3>${title}</h3><div>${body}</div></div>`;
    host.classList.add('show'); host.querySelector('.modal-close').addEventListener('click',()=>host.classList.remove('show'));
    host.addEventListener('click',e=>{if(e.target===host)host.classList.remove('show')},{once:true});
  };
  // Mobile navigation
  const toggle=$('#menu-toggle'); if(toggle) toggle.addEventListener('click',()=>{const nav=$('#mobile-nav'); const is=nav.classList.toggle('open'); toggle.setAttribute('aria-expanded',String(is)); toggle.textContent=is?'✕':'☰';});
  // Current page navigation
  const page=document.body.dataset.page;
  $$('[data-nav]').forEach(a=>{if(a.dataset.nav===page)a.classList.add('active')});
  // Favorite controls
  $$('.heart').forEach(btn=>btn.addEventListener('click',()=>{btn.classList.toggle('active');btn.textContent=btn.classList.contains('active')?'♥':'♡';toast(btn.classList.contains('active')?'Guardado en tus favoritos':'Eliminado de favoritos');}));
  // Add to cart
  let cart=Number(localStorage.getItem('sr-cart-count')||0);
  const cartCount=$('#cart-count'); if(cartCount)cartCount.textContent=cart;
  $$('.add-cart').forEach(btn=>btn.addEventListener('click',()=>{cart++;localStorage.setItem('sr-cart-count',String(cart));if(cartCount)cartCount.textContent=cart;toast('Producto añadido a tu pedido de demostración.');}));
  const cartBtn=$('#cart-button'); if(cartBtn)cartBtn.addEventListener('click',()=>openModal('Tu selección',`<p>Tienes <strong>${cart}</strong> producto(s) en tu carrito de demostración.</p><p>El checkout real se conectará con el backend, disponibilidad y pasarela de pago.</p><a class="btn btn-primary" href="ingresar.html">Continuar</a>`));
  // Search and category filtering
  const search=$('#catalog-search'); const cards=$$('[data-card]'); let selected='all';
  const applyFilters=()=>{const q=(search?.value||'').trim().toLowerCase();let count=0;cards.forEach(c=>{const matchText=(c.dataset.search||c.textContent).toLowerCase().includes(q);const matchCat=selected==='all'||c.dataset.category===selected;const show=matchText&&matchCat;c.hidden=!show;if(show)count++;});const counter=$('#results-count');if(counter)counter.textContent=`${count} resultados`;};
  if(search)search.addEventListener('input',applyFilters);
  $$('.filter-chip[data-filter]').forEach(b=>b.addEventListener('click',()=>{$$('.filter-chip[data-filter]').forEach(x=>x.classList.remove('active'));b.classList.add('active');selected=b.dataset.filter;applyFilters();}));
  const geo=$('#use-location'); if(geo)geo.addEventListener('click',()=>{if(!navigator.geolocation){toast('Este navegador no ofrece geolocalización.');return;}geo.disabled=true;geo.textContent='Consultando…';navigator.geolocation.getCurrentPosition(pos=>{geo.disabled=false;geo.textContent='Usar mi ubicación';toast(`Ubicación disponible para la demostración (${pos.coords.latitude.toFixed(2)}, ${pos.coords.longitude.toFixed(2)}).`);},()=>{geo.disabled=false;geo.textContent='Usar mi ubicación';toast('No se concedió acceso a la ubicación. Puedes buscar por distrito.');},{timeout:8000});});
  // AI discovery demo
  const aiForm=$('#ai-search-form'); if(aiForm)aiForm.addEventListener('submit',e=>{e.preventDefault();const q=$('#ai-query')?.value?.trim();if(!q){toast('Escribe qué te gustaría comer.');return;}const result=$('#ai-result');if(result){result.hidden=false;result.innerHTML=`<strong>Una idea para ti</strong><p>Interpretamos «${q.replace(/[<>]/g,'')}» como una búsqueda por antojo. Explora opciones reales usando los filtros de categoría, precio y ubicación.</p><a class="btn btn-primary btn-small" href="descubrir.html">Ver opciones sugeridas</a>`;}toast('Búsqueda interpretada en modo demostración.');});
  // Forms
  $$('form[data-demo-form]').forEach(form=>form.addEventListener('submit',e=>{e.preventDefault();if(!form.reportValidity())return;const kind=form.dataset.demoForm;if(kind==='login'){toast('Acceso de demostración: abre el ecosistema para probar los paneles.');setTimeout(()=>location.href='ecosistema-demo.html',700);}else if(kind==='register'){toast('Registro de demostración completado. La creación real de cuenta requiere backend.');form.reset();}else{toast('Gracias. El formulario se ha procesado en modo demostración.');form.reset();}}));
  // Pricing toggle
  const billing=$('#billing-toggle'); if(billing)billing.addEventListener('change',()=>{$$('.plan-price[data-monthly]').forEach(el=>{el.innerHTML=billing.checked?`${el.dataset.annual}<small> / año</small>`:`${el.dataset.monthly}<small> / mes</small>`;});});
  // 3D dish pointer rotation and portion slider
  const stage=$('#dish-stage'), dish=$('#dish'); if(stage&&dish){let down=false,lastX=0,lastY=0,rx=12,ry=-18;const render=()=>dish.style.transform=`rotateX(${rx}deg) rotateY(${ry}deg)`;stage.addEventListener('pointerdown',e=>{down=true;lastX=e.clientX;lastY=e.clientY;stage.setPointerCapture(e.pointerId);});stage.addEventListener('pointermove',e=>{if(!down)return;ry+=(e.clientX-lastX)*.65;rx-=(e.clientY-lastY)*.45;rx=Math.max(-35,Math.min(35,rx));lastX=e.clientX;lastY=e.clientY;render();});stage.addEventListener('pointerup',()=>down=false);stage.addEventListener('pointercancel',()=>down=false);$('#dish-reset')?.addEventListener('click',()=>{rx=12;ry=-18;render();});render();}
  const portion=$('#portion-range'); if(portion)portion.addEventListener('input',()=>{const value=Number(portion.value);const text=$('#portion-value');if(text)text.textContent=`${value} ${value===1?'porción':'porciones'}`;if(dish)dish.style.scale=String(.88+value*.045);});
  $('#ar-preview')?.addEventListener('click',()=>openModal('Vista de realidad aumentada',`<p>Esta vista es una demostración de la experiencia. La realidad aumentada real requiere un modelo 3D GLB calibrado, HTTPS, cámara y compatibilidad WebXR o una alternativa para iOS.</p><div class="ar-note">En el sistema conectado, el plato se visualizará sobre una superficie real respetando la escala que el negocio haya medido y validado.</div><button class="btn btn-primary" onclick="document.querySelector('#modal-backdrop').classList.remove('show')">Entendido</button>`));
  // Experience tabs
  $$('.experience-tab').forEach(btn=>btn.addEventListener('click',()=>{$$('.experience-tab').forEach(x=>x.classList.remove('active'));btn.classList.add('active');$$('[data-experience]').forEach(panel=>panel.hidden=panel.dataset.experience!==btn.dataset.target);}));
  // FAQ accordion
  $$('.faq-q').forEach(btn=>btn.addEventListener('click',()=>btn.closest('.faq-item').classList.toggle('open')));
  // Newsletter and social demo links
  $('#newsletter-form')?.addEventListener('submit',e=>{e.preventDefault();if(e.currentTarget.reportValidity())toast('Suscripción registrada en esta demostración.');e.currentTarget.reset();});
  $$('[data-social]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();toast('Añade aquí el enlace oficial de SmartResto en esta red.');}));
  // Cookie preferences: separate categories; no automatic location or push consent.
  const cookie=$('#cookie-banner'); const saved=localStorage.getItem('sr-cookie-choice'); if(cookie&&!saved)setTimeout(()=>cookie.classList.add('show'),900);
  $('#cookies-accept')?.addEventListener('click',()=>{localStorage.setItem('sr-cookie-choice','accepted');cookie?.classList.remove('show');toast('Preferencias de cookies guardadas.');});
  $('#cookies-reject')?.addEventListener('click',()=>{localStorage.setItem('sr-cookie-choice','essential');cookie?.classList.remove('show');toast('Solo se conservarán las cookies esenciales.');});
  $('#cookies-customize')?.addEventListener('click',()=>openModal('Preferencias de privacidad',`<p>Configura las categorías de almacenamiento. Las cookies no activan automáticamente la ubicación ni las notificaciones del navegador.</p><div class="modal-checks"><label><input type="checkbox" checked disabled> Esenciales — necesarias para la seguridad y navegación.</label><label><input type="checkbox" id="cookie-analytics"> Analítica — ayuda a mejorar el sitio.</label><label><input type="checkbox" id="cookie-personal"> Personalización — recuerda tus preferencias.</label></div><button class="btn btn-primary" id="save-cookie-settings">Guardar preferencias</button>`));
  document.addEventListener('click',e=>{if(e.target?.id==='save-cookie-settings'){localStorage.setItem('sr-cookie-choice',JSON.stringify({analytics:$('#cookie-analytics')?.checked,personal:$('#cookie-personal')?.checked}));$('#modal-backdrop')?.classList.remove('show');cookie?.classList.remove('show');toast('Preferencias personalizadas guardadas.');}});
  // Install PWA prompt where supported; otherwise give platform guidance.
  let installPrompt=null;window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();installPrompt=e;});
  $('#install-app')?.addEventListener('click',async()=>{if(installPrompt){installPrompt.prompt();await installPrompt.userChoice;installPrompt=null;}else openModal('Instala SmartResto',`<p><strong>Android / Chrome:</strong> abre el menú del navegador y selecciona «Instalar aplicación» o «Añadir a pantalla principal».</p><p><strong>iPhone / Safari:</strong> pulsa Compartir y elige «Añadir a pantalla de inicio».</p><p>La instalación y las notificaciones dependen del navegador, HTTPS y permisos disponibles.</p>`);});
  // Smooth scroll for in-page anchors
  $$('a[href^="#"]').forEach(a=>a.addEventListener('click',e=>{const target=$(a.getAttribute('href'));if(target){e.preventDefault();target.scrollIntoView({behavior:'smooth'});}}));

// Waitlist demonstration
$('#waitlist-demo')?.addEventListener('click',()=>openModal('Tu turno de demostración',`<div class="soft-panel" style="padding:18px"><span class="eyebrow">Sabor Norteño · Ejemplo</span><h2 class="serif" style="font-size:2.2rem;margin:8px 0">A-014</h2><strong>2 grupos delante de ti</strong><p class="muted">Espera estimada: 25–35 minutos. El turno real requerirá confirmación del restaurante y disponibilidad de una mesa compatible.</p></div><button class="btn btn-primary" id="confirm-waitlist" style="margin-top:15px">Confirmar interés</button>`));
document.addEventListener('click',e=>{if(e.target?.id==='confirm-waitlist'){document.querySelector('#modal-backdrop')?.classList.remove('show');toast('Interés confirmado en el turno de demostración.');}});
})();
