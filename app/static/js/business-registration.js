const form = document.getElementById('business-registration');

if (form) {
  for (const [name, id, fallback] of [
    ['restaurante', 'preview-name', 'Tu restaurante'],
    ['descripcion', 'preview-description', 'Tu propuesta gastronómica aparecerá aquí.'],
    ['distrito', 'preview-district', 'Tu distrito'],
  ]) {
    const update = () => { document.getElementById(id).textContent = form.elements[name].value.trim() || fallback; };
    form.elements[name].addEventListener('input', update);
    update();
  }

  document.getElementById('registration-error')?.focus();
  const privacy = form.elements.solo_distrito;
  const latitude = form.elements.latitud;
  const longitude = form.elements.longitud;
  const status = document.getElementById('location-status');
  const mapNode = document.getElementById('business-map');
  const styles = {
    dark: 'https://tiles.openfreemap.org/styles/liberty',
    light: 'https://tiles.openfreemap.org/styles/positron',
  };
  let map;
  let marker;

  const announce = text => { status.textContent = text; };
  const activeTheme = () => document.documentElement.dataset.theme === 'light' ? 'light' : 'dark';
  const coordinates = () => {
    if (!latitude.value || !longitude.value) return null;
    const point = [Number(longitude.value), Number(latitude.value)];
    return point.every(Number.isFinite) && Math.abs(point[0]) <= 90 && Math.abs(point[1]) <= 180 ? point : null;
  };
  const renderMarker = point => {
    if (!map) return;
    marker?.remove();
    marker = point ? new maplibregl.Marker({color: '#56d6c0'}).setLngLat(point).addTo(map) : null;
    if (point) map.flyTo({center: point, zoom: 15, essential: true});
  };

  if (window.maplibregl) {
    map = new maplibregl.Map({
      container: mapNode,
      style: styles[activeTheme()],
      center: coordinates() || [-79.0287, -8.1116],
      zoom: coordinates() ? 15 : 13,
      attributionControl: true,
    });
    map.addControl(new maplibregl.NavigationControl({showCompass: false}), 'top-right');
    map.on('load', () => renderMarker(coordinates()));
    map.on('click', event => {
      longitude.value = event.lngLat.lng.toFixed(6);
      latitude.value = event.lngLat.lat.toFixed(6);
      renderMarker(coordinates());
      announce('Punto seleccionado. Comprueba que corresponde al restaurante.');
    });
    map.on('error', event => {
      if (event.error?.status && event.error.status >= 400) announce('No se pudo cargar el mapa base. Puedes escribir las coordenadas manualmente.');
    });
    new MutationObserver(() => {
      if (!map) return;
      map.setStyle(styles[activeTheme()]);
      map.once('style.load', () => renderMarker(coordinates()));
    }).observe(document.documentElement, {attributes: true, attributeFilter: ['data-theme']});
  } else {
    announce('No se pudo cargar el mapa. Puedes escribir las coordenadas manualmente.');
  }

  for (const input of [latitude, longitude]) input.addEventListener('change', () => renderMarker(coordinates()));
  document.getElementById('clear-location').addEventListener('click', () => {
    latitude.value = '';
    longitude.value = '';
    renderMarker(null);
    announce('Punto eliminado.');
  });
  document.getElementById('locate-business').addEventListener('click', () => {
    if (!navigator.geolocation) {
      announce('Tu navegador no admite ubicación. Puedes seleccionar el punto en el mapa.');
      return;
    }
    announce('Obteniendo ubicación…');
    navigator.geolocation.getCurrentPosition(position => {
      latitude.value = position.coords.latitude.toFixed(6);
      longitude.value = position.coords.longitude.toFixed(6);
      renderMarker(coordinates());
      announce('Ubicación seleccionada. Comprueba que corresponde al restaurante.');
    }, () => announce('No se pudo obtener la ubicación. Puedes marcar el punto manualmente.'), {timeout: 10000});
  });
  const updatePrivacy = () => {
    document.getElementById('location-details').hidden = privacy.checked;
    form.elements.direccion.disabled = privacy.checked;
    form.elements.direccion.required = !privacy.checked;
    latitude.disabled = longitude.disabled = privacy.checked;
    if (!privacy.checked) setTimeout(() => map?.resize(), 0);
  };
  privacy.addEventListener('change', updatePrivacy);
  updatePrivacy();
  const submit = form.querySelector('[type="submit"]');
  const submitLabel = submit.textContent;
  form.addEventListener('submit', () => {
    submit.disabled = true;
    submit.textContent = 'Guardando…';
  });
  window.addEventListener('pageshow', () => {
    submit.disabled = false;
    submit.textContent = submitLabel;
  });
}
