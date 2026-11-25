/**
 * SmartResto - Mapa Leaflet
 */
let map = null;
let markers = {};
window.getLeafletMap = () => map;

function initMap() {
    if (document.body.classList.contains('sr-discover') && document.getElementById('forest-map-panel')?.hidden) return;
    const mapContainer = document.getElementById('main-map');
    if (!mapContainer) {
        console.warn('⚠️ Map container not found - skipping map initialization');
        return;
    }
    let center = [-8.1118, -79.0287];
    if (typeof INITIAL_COORDS !== 'undefined' && INITIAL_COORDS) center = INITIAL_COORDS;
    if (map) { map.remove(); map = null; }
    map = L.map('main-map').setView(center, 13);
    window._osmTilesState = 'loading';
    let loadedOsmTiles = 0;
    let failedOsmTiles = 0;
    const mapNotice = () => document.querySelector('.sr-map-dialog .sr-map-help');
    const osmTiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    });
    osmTiles.on('tileload', () => {
        loadedOsmTiles += 1;
        window._osmTilesState = 'ready';
        const notice = mapNotice();
        if (notice && /Descargando calles|Mapa gratuito|OpenStreetMap no entregó/.test(notice.textContent)) {
            notice.textContent = 'Calles de OpenStreetMap cargadas.';
        }
    });
    osmTiles.on('tileerror', event => {
        failedOsmTiles += 1;
        console.error('OpenStreetMap no pudo descargar una tesela:', event.tile?.src);
        if (loadedOsmTiles === 0 && failedOsmTiles >= 2) {
            window._osmTilesState = 'error';
            const notice = mapNotice();
            if (notice) notice.textContent = 'El mapa inició, pero OpenStreetMap no entregó las calles. Revisa la conexión, el firewall o un bloqueador.';
        }
    });
    osmTiles.addTo(map);
    if (window._pendingCenter) {
        map.setView([window._pendingCenter.lat, window._pendingCenter.lng], 15);
        delete window._pendingCenter;
    }
    const restaurantsToRender = window._pendingRestaurants || (typeof RESTAURANTS_DATA !== 'undefined' ? RESTAURANTS_DATA : null);
    if (Array.isArray(restaurantsToRender) && restaurantsToRender.length > 0) {
        updateMarkers(restaurantsToRender);
    }
    delete window._pendingRestaurants;
}

function updateMarkers(restaurants) {
    if (!map && window.mapGL) {
        const visibleIds = Array.isArray(restaurants)
            ? restaurants.map(restaurant => restaurant.id).filter(id => id != null)
            : null;
        window.mapGL.setVisible(visibleIds);
        return;
    }
    if (!map) {
        window._pendingRestaurants = restaurants;
        return;
    }
    Object.values(markers).forEach(m => {
        try { map.removeLayer(m); } catch (e) {}
    });
    markers = {};
    if (!restaurants || restaurants.length === 0) return;
    restaurants.forEach(r => {
        if (r.lat == null || r.lng == null || !Number.isSafeInteger(Number(r.id))) return;
        const marker = L.marker([r.lat, r.lng]).addTo(map);
        marker.bindPopup(`
            <div class="map-popup">
                <strong>${window.escapeDisplayText(r.name)}</strong><br>
                Rating: ${window.escapeDisplayText(r.rating)} ⭐<br>
                <a href="/negocio/${Number(r.id)}">Ver detalle</a>
            </div>
        `);
        markers[r.id] = marker;
    });
}

function highlightMarker(id) {
    if (markers[id]) markers[id].openPopup();
}
function resetMarker(id) {
    if (markers[id]) {
        setTimeout(() => { try { markers[id].closePopup(); } catch (e) {} }, 2000);
    }
}
function centerMap(lat, lng) {
    if (map) map.setView([lat, lng], 15);
    else window._pendingCenter = { lat, lng };
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('main-map')) initMap();
});

window.updateMarkers = updateMarkers;
window.centerMap = centerMap;
window.highlightMarkerOnMap = highlightMarker;
window.resetMarkerOnMap = resetMarker;

let userLocationMarker = null;
function addUserLocationMarker(lat, lng) {
    if (userLocationMarker) { map.removeLayer(userLocationMarker); userLocationMarker = null; }
    const userIcon = L.divIcon({
        className: 'user-location-marker',
        html: `<div style="width:20px;height:20px;background:var(--theme-info-bg);border-radius:50%;border:3px solid var(--theme-border);box-shadow:0 0 0 4px var(--theme-shadow),0 2px 8px var(--theme-shadow);animation:pulse 1.5s ease-in-out infinite;"></div>`,
        iconSize: [20, 20],
        iconAnchor: [10, 10]
    });
    userLocationMarker = L.marker([lat, lng], { icon: userIcon }).addTo(map);
    userLocationMarker.bindPopup('<i class="fas fa-map-marker-alt" aria-hidden="true"></i> Tu ubicación actual');
    if (window._userAccuracy) {
        L.circle([lat, lng], {
            radius: window._userAccuracy,
            color: window.SRTheme.color('info'),
            fillColor: window.SRTheme.color('info'),
            fillOpacity: 0.1,
            weight: 1
        }).addTo(map);
    }
    map.setView([lat, lng], 15);
}

window.getLeafletMap = () => map;
