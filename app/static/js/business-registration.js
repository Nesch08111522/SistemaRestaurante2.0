const form = document.getElementById('business-registration');
if (form) {
  for (const [name,id,fallback] of [['restaurante','preview-name','Tu restaurante'],['descripcion','preview-description','Tu propuesta gastronómica aparecerá aquí.'],['distrito','preview-district','Tu distrito']]) {
    const update = () => document.getElementById(id).textContent = form.elements[name].value.trim() || fallback;
    form.elements[name].addEventListener('input',update); update();
  }
  document.getElementById('registration-error')?.focus();
  const privacy = form.elements.solo_distrito;
  const lat = form.elements.latitud, lon = form.elements.longitud;
  const status = document.getElementById('location-status');
  let map, marker;
  function coordinates() {
    if (!lat.value || !lon.value) return null;
    const point = [Number(lat.value), Number(lon.value)];
    return point.every(Number.isFinite) && Math.abs(point[0])<=90 && Math.abs(point[1])<=180 ? point : null;
  }
  function pin(point) {
    if (!map) return;
    if (marker) map.removeLayer(marker);
    marker = point ? L.marker(point).addTo(map) : null;
    if(point) map.setView(point,15);
  }
  if (window.L) {
    map = L.map('business-map').setView(coordinates() || [-8.1116,-79.0287],13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'&copy; OpenStreetMap contributors',maxZoom:19}).addTo(map);
    map.on('click', e => { lat.value=e.latlng.lat.toFixed(6); lon.value=e.latlng.lng.toFixed(6); pin(coordinates()); });
    pin(coordinates());
  }
  for (const input of [lat,lon]) input.addEventListener('change', () => pin(coordinates()));
  document.getElementById('clear-location').addEventListener('click',()=>{lat.value='';lon.value='';pin(null);status.textContent='Punto eliminado.';});
  document.getElementById('locate-business').addEventListener('click',()=>{
    if(!navigator.geolocation) {status.textContent='Tu navegador no admite ubicación. Puedes seleccionar el punto en el mapa.';return;}
    status.textContent='Obteniendo ubicación…';
    navigator.geolocation.getCurrentPosition(p=>{
      lat.value=p.coords.latitude.toFixed(6);lon.value=p.coords.longitude.toFixed(6);pin(coordinates());status.textContent='Ubicación seleccionada. Comprueba que corresponde al restaurante.';
    },()=>{status.textContent='No se pudo obtener la ubicación. Puedes marcar el punto manualmente.';},{timeout:10000});
  });
  function privacyChanged() {
    document.getElementById('location-details').hidden=privacy.checked;
    form.elements.direccion.disabled=privacy.checked;
    form.elements.direccion.required=!privacy.checked;
    lat.disabled=lon.disabled=privacy.checked;
    if(!privacy.checked) setTimeout(()=>map?.invalidateSize(),0);
  }
  privacy.addEventListener('change',privacyChanged);privacyChanged();
  const submitLabel = form.querySelector('[type="submit"]').textContent;
  form.addEventListener('submit',()=>{
    const submit=form.querySelector('[type="submit"]');submit.disabled=true;submit.textContent='Guardando…';
  });
  window.addEventListener('pageshow',()=>{const submit=form.querySelector('[type="submit"]');submit.disabled=false;submit.textContent=submitLabel;});
}
