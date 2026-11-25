(() => {
  const cards = document.querySelectorAll('[data-ticket]');
  function track(card, stage) {
    fetch('/mercado/interaccion', {method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({ticket:card.dataset.ticket, stage})}).catch(() => {});
  }
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const e of entries) if (e.isIntersecting) { track(e.target,'viewed'); observer.unobserve(e.target); }
    }, {threshold:.3});
    for (const card of cards) observer.observe(card);
  }
  const mapNode = document.getElementById('market-map');
  if (mapNode && window.L) {
    try {
      const pins = JSON.parse(document.getElementById('market-pins').textContent);
      const map = L.map(mapNode);
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {attribution:'© OpenStreetMap contributors'}).addTo(map);
      const bounds = L.latLngBounds([]);
      for (const pin of pins) {
        const text = document.createElement('span');
        text.textContent = [pin.name, pin.pickup].filter(Boolean).join(' · ');
        L.marker(pin.point).addTo(map).bindPopup(text);
        bounds.extend(pin.point);
      }
      if (pins.length) map.fitBounds(bounds, {maxZoom:15, padding:[16,16]});
    } catch (_) {}
  }
})();
