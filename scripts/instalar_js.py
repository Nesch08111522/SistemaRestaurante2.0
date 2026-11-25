"""
Instala los 30 JS de SmartResto en app/static/js/.
Ejecutar: python scripts\\instalar_js.py
"""
from pathlib import Path

JS_DIR = Path(__file__).parent.parent / "app" / "static" / "js"
JS_DIR.mkdir(parents=True, exist_ok=True)

FILES = {}

# ============================================================
# 1. theme.js
# ============================================================
FILES["theme.js"] = r"""/* Theme toggle: persiste en localStorage y respeta prefers-color-scheme. */
(function () {
  'use strict';
  const root = document.documentElement;
  const KEY = 'theme';
  const buttons = () => document.querySelectorAll('[data-theme-toggle]');
  function read() {
    try { return localStorage.getItem(KEY) === 'light' ? 'light' : 'dark'; }
    catch (_) { return 'dark'; }
  }
  function apply(theme) {
    root.dataset.theme = theme;
    root.style.colorScheme = theme;
    document.dispatchEvent(new CustomEvent('themechange', {detail: {theme}}));
    buttons().forEach(btn => {
      const isDark = theme === 'dark';
      btn.setAttribute('aria-pressed', String(isDark));
      btn.setAttribute('aria-label', isDark ? 'Activar tema claro' : 'Activar tema oscuro');
      const label = btn.querySelector('[data-theme-label]');
      if (label) label.textContent = isDark ? 'Usar tema claro' : 'Usar tema oscuro';
      const icon = btn.querySelector('[data-theme-icon]');
      if (icon) icon.textContent = isDark ? '☀' : '☾';
    });
  }
  function toggle() {
    const next = read() === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem(KEY, next); } catch (_) {}
    apply(next);
  }
  function boot() {
    buttons().forEach(btn => {
      if (btn.dataset.themeBound) return;
      btn.dataset.themeBound = '1';
      btn.addEventListener('click', toggle);
    });
    apply(read());
  }
  window.SRTheme = {
    color(name) {
      return getComputedStyle(root).getPropertyValue('--theme-' + name).trim() || 'inherit';
    }
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, {once: true});
  else boot();
  window.addEventListener('storage', e => { if (e.key === KEY) apply(read()); });
})();
"""

# ============================================================
# 2. shell.js
# ============================================================
FILES["shell.js"] = r"""(() => {
    const root = document.documentElement;
    try {
        if (localStorage.getItem('sr-sidebar-state') === 'expanded') root.classList.remove('sr-compact');
        else root.classList.add('sr-compact');
    } catch {
        root.classList.add('sr-compact');
    }

    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('.filter-chip').forEach(chip => {
            chip.setAttribute('aria-pressed', String(chip.classList.contains('active')));
        });
        document.querySelectorAll('.sr-filter-form').forEach(form => {
            const fields = [...form.querySelectorAll('.sr-filter-fields input, .sr-filter-fields select')];
            const count = form.querySelector('[data-filter-count]');
            if (!count) return;
            function updateFilterCount() {
                const active = fields.filter(field => field.type === 'checkbox' ? field.checked : field.value.trim() !== '').length;
                count.textContent = active ? ` (${active})` : '';
            }
            form.addEventListener('input', updateFilterCount);
            form.addEventListener('change', updateFilterCount);
            updateFilterCount();
        });

        let drag;
        let suppressClick = false;
        document.addEventListener('pointerdown', event => {
            suppressClick = false;
            if (!(event.target instanceof Element) || event.pointerType !== 'mouse' || event.button !== 0 || event.shiftKey ||
                event.target.closest('a[href],input,textarea,select,button,summary,[role=button],[role=link],[contenteditable=true],.private-account,.map-container,.leaflet-container,.maplibregl-map')) return;
            const candidates = [];
            for (let el = event.target; el && el !== document.documentElement; el = el.parentElement) {
                const css = getComputedStyle(el);
                if (/auto|scroll/.test(css.overflowY) && el.scrollHeight > el.clientHeight ||
                    /auto|scroll/.test(css.overflowX) && el.scrollWidth > el.clientWidth) candidates.push(el);
            }
            candidates.push(document.scrollingElement);
            drag = {id:event.pointerId, x:event.clientX, y:event.clientY, candidates};
        });
        document.addEventListener('pointermove', event => {
            if (!drag || drag.id !== event.pointerId || !event.buttons) return;
            const dx = event.clientX - drag.x, dy = event.clientY - drag.y;
            if (!drag.target) {
                if (Math.max(Math.abs(dx), Math.abs(dy)) < 7) return;
                const horizontal = Math.abs(dx) > Math.abs(dy);
                drag.target = drag.candidates.find(el => horizontal ? el.scrollWidth > el.clientWidth : el.scrollHeight > el.clientHeight);
                if (!drag.target) return;
                drag.left = drag.target.scrollLeft;
                drag.top = drag.target.scrollTop;
                root.classList.add('sr-dragging');
                window.getSelection()?.removeAllRanges();
                drag.target.setPointerCapture(event.pointerId);
            }
            event.preventDefault();
            drag.target.scrollTo(drag.left - dx, drag.top - dy);
        });
        function endDrag() {
            suppressClick = Boolean(drag?.target);
            root.classList.remove('sr-dragging');
            drag = null;
        }
        document.addEventListener('pointerup', endDrag);
        document.addEventListener('pointercancel', endDrag);
        window.addEventListener('blur', endDrag);
        document.addEventListener('click', event => {
            if (suppressClick && event.detail && event.target instanceof Element &&
                !event.target.closest('a[href],button,input,select,textarea,summary,[role=button],[role=link]')) {
                event.preventDefault(); event.stopImmediatePropagation();
            }
            suppressClick = false;
        }, true);

        const counters = document.querySelector('[data-counts-url]');
        if (counters) {
            async function refresh() {
                if (document.hidden) return;
                try {
                    const response = await fetch(counters.dataset.countsUrl, {cache:'no-store'});
                    if (!response.ok) return;
                    const counts = await response.json();
                    counters.querySelectorAll('[data-count]').forEach(node => {
                        if (node.dataset.count === 'notificaciones' && window.srNotificationFeed) return;
                        const count = counts[node.dataset.count] || 0;
                        node.textContent = String(count);
                        node.hidden = count === 0;
                    });
                } catch { /* silencioso */ }
            }
            refresh();
            const timer = setInterval(refresh, 30000);
            document.addEventListener('visibilitychange', refresh);
            window.addEventListener('pagehide', () => clearInterval(timer), {once:true});
        }

        const account = document.querySelector('[data-account-toggle]');
        const options = document.getElementById('private-account-menu');
        function accountOpen(value, restore = false) {
            if (!options || !account) return;
            options.hidden = !value;
            account.setAttribute('aria-expanded', String(value));
            if (value) options.querySelector('a')?.focus();
            else if (restore) account.focus();
        }
        account?.addEventListener('click', () => accountOpen(options.hidden));
        document.addEventListener('click', event => {
            if (!event.target.closest('.private-account')) accountOpen(false);
        });
        document.addEventListener('keydown', event => {
            if (event.key === 'Escape' && options && !options.hidden) {
                event.preventDefault(); event.stopImmediatePropagation(); accountOpen(false, true);
            }
        }, true);
        options?.addEventListener('focusout', event => {
            if (event.relatedTarget instanceof Element && !event.relatedTarget.closest('.private-account')) accountOpen(false);
        });
        document.querySelector('.sr-menu-button')?.addEventListener('click', () => accountOpen(false), true);
        window.addEventListener('pagehide', () => accountOpen(false));

        if (document.body.classList.contains('sr-private')) return;

        const menu = document.getElementById('sr-navigation');
        const trigger = document.querySelector('.sr-menu-button');
        const backdrop = document.querySelector('.sr-backdrop');
        const collapse = document.querySelector('.sr-collapse');
        if (!menu || !trigger || !backdrop) return;

        const wide = matchMedia('(min-width: 1100px)');
        const isDesktopPanel = () => wide.matches && menu.classList.contains('sr-sidebar');

        function updateCollapse() {
            if (!collapse) return;
            const compact = root.classList.contains('sr-compact') && !root.classList.contains('sr-nav-preview');
            const label = isDesktopPanel() ? (root.classList.contains('sr-compact') ? (compact ? 'Expandir menú' : 'Fijar menú abierto') : 'Contraer menú') : 'Cerrar menú';
            collapse.setAttribute('aria-controls', 'sr-navigation');
            collapse.setAttribute('aria-expanded', String(isDesktopPanel() ? !compact : root.classList.contains('sr-drawer-open')));
            collapse.title = label;
            collapse.setAttribute('aria-label', label);
            collapse.textContent = isDesktopPanel() ? (compact ? '⇥' : '⇤') : '×';
        }

        function drawer(open, restoreFocus = true) {
            root.classList.toggle('sr-drawer-open', open);
            backdrop.hidden = !open;
            updateCollapse();
            trigger.setAttribute('aria-expanded', String(open));
            trigger.setAttribute('aria-label', open ? 'Cerrar navegación' : 'Abrir navegación');
            const areas = document.querySelectorAll('#main-content, .sr-footer, .sr-mobile-nav');
            areas.forEach(area => { area.inert = open; });
            if (open) {
                menu.setAttribute('role', 'dialog');
                menu.setAttribute('aria-modal', 'true');
                (collapse || menu).focus();
            } else {
                menu.removeAttribute('role');
                menu.removeAttribute('aria-modal');
                if (restoreFocus) trigger.focus();
            }
        }

        trigger.addEventListener('click', () => {
            drawer(!root.classList.contains('sr-drawer-open'));
        });
        backdrop.addEventListener('click', () => drawer(false));

        if (collapse) {
            collapse.addEventListener('click', () => {
                if (!isDesktopPanel()) return drawer(false);
                root.classList.toggle('sr-compact');
                try { localStorage.setItem('sr-sidebar-state', root.classList.contains('sr-compact') ? 'collapsed' : 'expanded'); } catch {}
                updateCollapse();
            });
        }

        document.addEventListener('keydown', event => {
            if (!(event.ctrlKey || event.metaKey) || event.altKey || event.key.toLowerCase() !== 'b') return;
            event.preventDefault();
            if (!isDesktopPanel()) return drawer(!root.classList.contains('sr-drawer-open'));
            root.classList.toggle('sr-compact');
            try { localStorage.setItem('sr-sidebar-state', root.classList.contains('sr-compact') ? 'collapsed' : 'expanded'); } catch {}
            updatePreview();
        });

        let pointerInside = false;
        function updatePreview() {
            const keyboardInside = Boolean(menu.querySelector(':focus-visible'));
            root.classList.toggle('sr-nav-preview', isDesktopPanel() && (pointerInside || keyboardInside));
            updateCollapse();
        }
        menu.addEventListener('pointerenter', event => {
            if (event.pointerType !== 'mouse') return;
            pointerInside = true;
            updatePreview();
        });
        menu.addEventListener('pointerleave', () => {
            pointerInside = false;
            updatePreview();
        });
        menu.addEventListener('focusin', updatePreview);
        menu.addEventListener('focusout', () => requestAnimationFrame(updatePreview));
        wide.addEventListener('change', () => {
            pointerInside = false;
            drawer(false, false);
            updatePreview();
        });

        drawer(false, false);
        updateCollapse();

        document.addEventListener('keydown', event => {
            if (!root.classList.contains('sr-drawer-open')) return;
            if (event.key === 'Escape') return drawer(false);
            if (event.key !== 'Tab') return;
            const items = [...menu.querySelectorAll('button, a[href], summary')].filter(item => item.getClientRects().length);
            if (!items.length) return;
            if (event.shiftKey && document.activeElement === items[0]) { event.preventDefault(); items.at(-1).focus(); }
            if (!event.shiftKey && document.activeElement === items.at(-1)) { event.preventDefault(); items[0].focus(); }
        });

        const toggle = document.querySelector('#recommendationBtn');
        const modal = document.querySelector('#recommendationModal');
        if (toggle && modal && !document.body.classList.contains('sr-discover')) {
            toggle.addEventListener('click', () => requestAnimationFrame(() => modal.querySelector('textarea')?.focus()));
            document.addEventListener('keydown', event => {
                if (event.key === 'Escape' && modal.style.display === 'flex') {
                    modal.querySelector('.close-modal')?.click();
                    toggle.focus();
                }
            });
        }
    });
})();
"""

# ============================================================
# 3. private-shell.js
# ============================================================
FILES["private-shell.js"] = r"""(() => {
  document.addEventListener('DOMContentLoaded', () => {
    if (!document.body.classList.contains('sr-private')) return;
    document.querySelectorAll('#main-content table').forEach(table => {
      let container = table.closest('.table-container,.cat-table-wrap,.mgr-table,.table-responsive,.catalog-table-wrap,.admin-scroll,.workspace-scroll');
      if (!container) {
        container = document.createElement('div');
        container.className = 'workspace-scroll';
        table.before(container);
        container.append(table);
      }
      container.tabIndex = 0;
      container.setAttribute('role', 'region');
      container.setAttribute('aria-label', table.caption?.textContent.trim() || 'Tabla de datos, desplazamiento horizontal');
    });
    const root = document.documentElement;
    const menu = document.getElementById('sr-navigation');
    const trigger = document.querySelector('.sr-menu-button');
    if (!menu || !trigger) return;
    const close = menu.querySelector('.sr-collapse');
    const backdrop = document.querySelector('.sr-backdrop');
    const wide = matchMedia('(min-width:1100px)');
    const account = document.querySelector('[data-account-toggle]');
    const options = document.getElementById('private-account-menu');
    let open = false;
    const areas = [...document.querySelectorAll('#main-content,.sr-header,.sr-footer,.sr-mobile-nav')];
    const previous = new Map();
    function accountOpen(value, restore = false) {
      if (!options || !account) return;
      options.hidden = !value;
      account.setAttribute('aria-expanded', String(value));
      if (value) options.querySelector('a').focus();
      else if (restore) account.focus();
    }
    function drawer(value, restore = true) {
      open = value && !wide.matches;
      root.classList.toggle('sr-drawer-open', open);
      root.classList.remove('sr-nav-preview');
      backdrop.hidden = !open;
      menu.inert = !wide.matches && !open;
      trigger.setAttribute('aria-expanded', String(wide.matches ? !root.classList.contains('sr-compact') : open));
      const expanded = wide.matches && !root.classList.contains('sr-compact');
      const label = wide.matches ? (expanded ? 'Contraer menu' : 'Expandir menu') : 'Cerrar navegacion';
      close.setAttribute('aria-label', label);
      close.setAttribute('aria-expanded', String(wide.matches ? expanded : open));
      close.title = label;
      trigger.setAttribute('aria-label', open ? 'Cerrar navegacion' : 'Abrir navegacion');
      if (open) {
        accountOpen(false);
        menu.setAttribute('role', 'dialog');
        menu.setAttribute('aria-modal', 'true');
        areas.forEach(area => { if (!previous.has(area)) previous.set(area, area.inert); area.inert = true; });
        close.focus();
      } else {
        menu.removeAttribute('role');
        menu.removeAttribute('aria-modal');
        previous.forEach((value, area) => { area.inert = value; });
        previous.clear();
        if (restore) trigger.focus();
      }
    }
    function toggle() {
      if (!wide.matches) return drawer(!open);
      root.classList.toggle('sr-compact');
      try { localStorage.setItem('sr-sidebar-state', root.classList.contains('sr-compact') ? 'collapsed' : 'expanded'); } catch (_) {}
      drawer(false, false);
    }
    [trigger, close, backdrop].forEach(button => button.addEventListener('click', event => {
      event.preventDefault(); event.stopImmediatePropagation();
      if (button === backdrop || (button === close && !wide.matches)) drawer(false);
      else toggle();
    }, true));
    menu.addEventListener('click', event => { if (open && event.target.closest('a')) drawer(false, false); });
    document.addEventListener('keydown', event => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'b') { event.preventDefault(); event.stopImmediatePropagation(); toggle(); }
      if (!open) return;
      if (event.key === 'Escape') { event.stopImmediatePropagation(); drawer(false); }
      if (event.key !== 'Tab') return;
      const items = [...menu.querySelectorAll('a,button,summary')].filter(node => node.getClientRects().length);
      const first = items[0], last = items.at(-1);
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }, true);
    wide.addEventListener('change', () => drawer(false, false));
    window.addEventListener('pagehide', () => { drawer(false, false); accountOpen(false); });
    window.addEventListener('pageshow', () => drawer(false, false));
    drawer(false, false);
  });
})();
"""

# ============================================================
# 4. security.js
# ============================================================
FILES["security.js"] = r"""/* Seguridad transversal de formularios y APIs same-origin. */
(function () {
  'use strict';
  window.escapeDisplayText = function (value) {
    const entities = {'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'};
    return String(value ?? '').replace(/[&<>"']/g, ch => entities[ch]);
  };
  function token() {
    const element = document.querySelector('meta[name="csrf-token"]');
    return element ? element.getAttribute('content') : '';
  }
  function isMutating(method) {
    return ['POST', 'PUT', 'PATCH', 'DELETE'].includes((method || 'GET').toUpperCase());
  }
  const nativeFetch = window.fetch.bind(window);
  window.fetch = function (input, init) {
    const options = init ? { ...init } : {};
    const method = (options.method || (input && input.method) || 'GET').toUpperCase();
    const url = input instanceof Request ? input.url : String(input);
    const sameOrigin = new URL(url, document.baseURI).origin === window.location.origin;
    if (sameOrigin && isMutating(method)) {
      const headers = new Headers(options.headers || (input instanceof Request ? input.headers : undefined));
      const csrfToken = token();
      if (csrfToken) headers.set('X-CSRFToken', csrfToken);
      options.headers = headers;
    }
    return nativeFetch(input, options);
  };
  document.addEventListener('DOMContentLoaded', function () {
    const csrfToken = token();
    if (!csrfToken) return;
    document.querySelectorAll('form').forEach(function (form) {
      const method = (form.getAttribute('method') || 'GET').toUpperCase();
      if (new URL(form.action, document.baseURI).origin !== window.location.origin) return;
      if (!isMutating(method) || form.querySelector('input[name="csrf_token"]')) return;
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = 'csrf_token';
      input.value = csrfToken;
      form.appendChild(input);
    });
  });
})();
"""

# ============================================================
# 5. responsive-layout.js
# ============================================================
FILES["responsive-layout.js"] = r"""/* Add internal horizontal scrolling around data tables where markup has no wrapper. */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('table').forEach((table) => {
    let wrapper = table.closest('.table-responsive, .table-container, .table-wrapper, .mgr-table');
    if (!wrapper) {
      wrapper = document.createElement('div');
      wrapper.className = 'table-responsive';
      table.parentNode.insertBefore(wrapper, table);
      wrapper.appendChild(table);
    }
    if (!wrapper.hasAttribute('tabindex')) wrapper.setAttribute('tabindex', '0');
    if (!wrapper.hasAttribute('role')) wrapper.setAttribute('role', 'region');
    if (!wrapper.hasAttribute('aria-label') && !wrapper.hasAttribute('aria-labelledby')) {
      wrapper.setAttribute('aria-label', table.caption?.textContent.trim() || table.getAttribute('aria-label') || 'Tabla desplazable horizontalmente');
    }
  });
});
"""

# ============================================================
# 6. layout-system.js
# ============================================================
FILES["layout-system.js"] = r"""/* Progressive, reduced-motion-safe reveal for shared layout components. */
(function () {
  'use strict';
  const targets = document.querySelectorAll('[data-layout-reveal]');
  if (!targets.length || !('IntersectionObserver' in window) || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.documentElement.classList.add('layout-observe');
  const observer = new IntersectionObserver((entries, current) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      current.unobserve(entry.target);
    });
  }, { rootMargin: '0px 0px -32px 0px', threshold: 0.08 });
  targets.forEach(target => observer.observe(target));
})();
"""

# ============================================================
# 7. map.js
# ============================================================
FILES["map.js"] = r"""/**
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
"""

# ============================================================
# 8. search.js
# ============================================================
FILES["search.js"] = r"""/**
 * SmartResto - Búsqueda y Filtros en Tiempo Real
 */
const SEARCH_CONFIG = {
    debounceDelay: 300,
    maxResults: 20,
    minQueryLength: 2
};
function debounce(fn, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn.apply(this, args), delay);
    };
}
const FilterFunctions = {
    byText: (restaurants, query) => {
        if (!query || query.length < SEARCH_CONFIG.minQueryLength) return restaurants;
        const q = query.toLowerCase();
        return restaurants.filter(r => 
            r.name.toLowerCase().includes(q) ||
            r.description?.toLowerCase().includes(q) ||
            r.tags?.some(tag => tag.toLowerCase().includes(q)) ||
            r.district?.toLowerCase().includes(q)
        );
    },
    byCategory: (restaurants, categoryId) => {
        if (!categoryId) return restaurants;
        return restaurants.filter(r => r.category_id == categoryId);
    },
    byDistrict: (restaurants, district) => {
        if (!district) return restaurants;
        return restaurants.filter(r => r.district === district);
    },
    byPrice: (restaurants, maxPrice) => {
        if (!maxPrice || maxPrice <= 0) return restaurants;
        return restaurants.filter(r => r.avg_price <= maxPrice);
    }
};
class RealTimeSearch {
    constructor() {
        this.searchForm = document.getElementById('search-form');
        this.resultsGrid = document.getElementById('resultsGrid');
        this.resultsCount = document.getElementById('resultsCount');
        this.isLoading = false;
        this.init();
    }
    init() {
        if (this.searchForm) {
            this.searchForm.addEventListener('input', () => this.controller?.abort());
            this.searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.performSearch();
            });
            const searchInput = this.searchForm.querySelector('input[name="q"]');
            if (searchInput) {
                searchInput.addEventListener('input', debounce(() => this.performSearch(), SEARCH_CONFIG.debounceDelay));
            }
            const selects = this.searchForm.querySelectorAll('select');
            selects.forEach(select => select.addEventListener('change', () => this.performSearch()));
            const priceInput = this.searchForm.querySelector('input[name="max_price"]');
            if (priceInput) priceInput.addEventListener('input', debounce(() => this.performSearch(), SEARCH_CONFIG.debounceDelay));
        }
    }
    async performSearch() {
        this.controller?.abort();
        const controller = new AbortController();
        this.controller = controller;
        const formData = new FormData(this.searchForm);
        const district = document.getElementById('district-select')?.value || '';
        const category = document.getElementById('category-select')?.value || '';
        const maxPrice = document.querySelector('input[name="max_price"]')?.value || '';
        const query = formData.get('q') || '';
        const filters = {
            district: district,
            category_id: category ? parseInt(category) : null,
            max_price: maxPrice ? parseFloat(maxPrice) : null,
            search_query: query,
            lat: typeof INITIAL_COORDS !== 'undefined' ? INITIAL_COORDS[0] : -8.1118,
            lng: typeof INITIAL_COORDS !== 'undefined' ? INITIAL_COORDS[1] : -79.0287
        };
        this.showLoading();
        try {
            const response = await fetch('/descubrir/api/restaurants', {
                method: 'POST',
                signal: controller.signal,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(filters)
            });
            if (!response.ok) throw new Error("search");
            const data = await response.json();
            if (controller.signal.aborted) return;
            const results = Array.isArray(data) ? data : (Array.isArray(data.results) ? data.results : []);
            this.updateResults(results);
            this.updateMapMarkers(results);
        } catch (error) {
            if (controller.signal.aborted) return;
            console.error('Error en la búsqueda:', error);
            this.showError('Error al realizar la búsqueda.');
        } finally {
            if (this.controller === controller) this.hideLoading();
        }
    }
    updateResults(results) {
        const grid = this.resultsGrid;
        if (!grid) return;
        if (this.resultsCount) this.resultsCount.textContent = `${results.length} restaurantes encontrados`;
        if (results.length === 0) {
            grid.innerHTML = `<div class="empty-state"><i class="fas fa-utensils"></i><h3>No encontramos restaurantes</h3><p>Intenta con otros filtros.</p></div>`;
            return;
        }
        if (window.app) {
            window.app.state.filteredRestaurants = results;
            window.app.renderRestaurants();
        }
    }
    updateMapMarkers(restaurants) {
        if (typeof window.updateMarkers === 'function') window.updateMarkers(restaurants);
    }
    showLoading() { this.isLoading = true; }
    hideLoading() { this.isLoading = false; }
    showError(message) {
        const grid = this.resultsGrid;
        if (grid) grid.innerHTML = `<div class="empty-state"><i class="fas fa-exclamation-triangle"></i><h3>Error</h3><p>${message}</p></div>`;
    }
}
document.addEventListener('DOMContentLoaded', () => {
    window.search = new RealTimeSearch();
});
window.performSearch = function() {
    if (window.search) window.search.performSearch();
};
"""

# ============================================================
# 9. app.js (versión simplificada funcional)
# ============================================================
FILES["app.js"] = r"""class AppController {
    constructor() {
        this.state = {
            restaurants: [],
            filteredRestaurants: [],
            currentView: 'grid',
            favorites: [],
            user: null,
            theme: document.documentElement.dataset.theme || 'dark'
        };
        this.elements = {};
        this.init();
    }
    init() {
        this.elements = {
            resultsGrid: document.getElementById('resultsGrid'),
            resultsCount: document.getElementById('resultsCount'),
            searchForm: document.getElementById('search-form'),
            themeToggle: document.getElementById('themeToggle'),
            locationBtn: document.getElementById('locationBtn'),
            loadMoreBtn: document.getElementById('loadMoreBtn'),
            recommendationBtn: document.getElementById('recommendationBtn'),
            recommendationModal: document.getElementById('recommendationModal'),
            recommendationForm: document.getElementById('recommendationForm'),
            notificationBtn: document.getElementById('notificationsBtn'),
            notificationPanel: document.getElementById('notificationPanel'),
            userMenuBtn: document.getElementById('userMenuBtn'),
            userDropdown: document.getElementById('userDropdown')
        };
        this.loadState();
        this.loadFavorites();
        this.bindEvents();
        this.loadRestaurants();
    }
    loadState() {
        this.state.favorites = [];
        const savedLat = localStorage.getItem('userLat');
        const savedLng = localStorage.getItem('userLng');
        if (savedLat && savedLng) {
            this.state.userLocation = { lat: parseFloat(savedLat), lng: parseFloat(savedLng) };
        }
    }
    saveState() {
        document.querySelectorAll('.fav-btn').forEach(button => {
            const id = Number(button.dataset.restaurantId || button.closest('[data-id]')?.dataset.id);
            const active = this.state.favorites.includes(id);
            button.classList.toggle('active', active);
            button.setAttribute('aria-pressed', String(active));
        });
    }
    bindEvents() {
        this.elements.locationBtn?.addEventListener('click', () => this.getUserLocation());
        this.elements.loadMoreBtn?.addEventListener('click', () => this.loadMoreRestaurants());
        this.elements.recommendationBtn?.addEventListener('click', (e) => {
            e.preventDefault();
            this.openRecommendationModal();
        });
        document.querySelector('.close-modal')?.addEventListener('click', () => this.closeRecommendationModal());
        this.elements.recommendationForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.getRecommendations();
        });
        this.elements.notificationBtn?.addEventListener('click', () => this.toggleNotifications());
        this.elements.userMenuBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            this.elements.userDropdown?.classList.toggle('show');
        });
        document.addEventListener('click', () => this.elements.userDropdown?.classList.remove('show'));
        document.querySelectorAll('.filter-chip').forEach(chip => {
            chip.addEventListener('click', () => this.applyFilter(chip));
        });
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', () => this.changeView(btn.dataset.view));
        });
    }
    loadRestaurants() {
        if (typeof RESTAURANTS_DATA !== 'undefined') {
            this.state.restaurants = RESTAURANTS_DATA;
            this.state.filteredRestaurants = RESTAURANTS_DATA;
            this.renderRestaurants();
        }
    }
    renderRestaurants() {
        const grid = this.elements.resultsGrid;
        if (!grid) return;
        if (this.state.filteredRestaurants.length === 0) {
            if (this.elements.resultsCount) this.elements.resultsCount.textContent = '0 restaurantes encontrados';
            grid.innerHTML = `<div class="empty-state"><i class="fas fa-utensils"></i><h3>No encontramos restaurantes</h3><p>Intenta con otros filtros.</p></div>`;
            return;
        }
        const visible = this.state.filteredRestaurants.slice(0, 12);
        grid.innerHTML = visible.map(r => this.renderRestaurantCard(r)).join('');
        if (this.elements.resultsCount) {
            this.elements.resultsCount.textContent = `${this.state.filteredRestaurants.length} restaurantes encontrados`;
        }
    }
    renderRestaurantCard(restaurant) {
        if (document.body.classList.contains('sr-discover') && window.ForestUI) {
            return window.ForestUI.renderRestaurantCard(restaurant, this.state.favorites, typeof MONEDA !== 'undefined' ? MONEDA : 'S/');
        }
        if (!Number.isSafeInteger(Number(restaurant.id))) return "";
        const esc = window.escapeDisplayText;
        return `<div class="restaurant-card" data-id="${Number(restaurant.id)}"><div class="card-content"><h3>${esc(restaurant.name)}</h3></div></div>`;
    }
    applyFilter(chip) {
        document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        this.state.filteredRestaurants = this.state.restaurants.filter(r => !chip.dataset.category || String(r.category_id) === String(chip.dataset.category));
        this.renderRestaurants();
    }
    changeView(view) { this.state.currentView = view; }
    openRecommendationModal() {
        const modal = this.elements.recommendationModal;
        if (modal) { modal.style.display = 'flex'; modal.classList.add('show'); }
    }
    closeRecommendationModal() {
        const modal = this.elements.recommendationModal;
        if (modal) { modal.style.display = 'none'; modal.classList.remove('show'); }
    }
    async getRecommendations() {
        const form = this.elements.recommendationForm;
        if (!form) return;
        const formData = new FormData(form);
        const data = {
            location: formData.get('location') || '',
            budget: parseFloat(formData.get('budget')) || 0,
            food_preference: parseInt(formData.get('food_preference')) || 0,
            visit_time: formData.get('visit_time') || '',
            restrictions: formData.getAll('restrictions'),
            goal: formData.get('goal') || ''
        };
        if (this.state.userLocation) {
            data.lat = this.state.userLocation.lat;
            data.lng = this.state.userLocation.lng;
        }
        try {
            const response = await fetch('/descubrir/api/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (result.recomendacion?.items?.length) {
                this.closeRecommendationModal();
                alert(`¡Encontramos ${result.recomendacion.items.length} recomendaciones!`);
            } else {
                alert('No encontramos coincidencias.');
            }
        } catch (error) {
            console.error('Error en recomendación:', error);
            alert('Error al obtener recomendaciones.');
        }
    }
    getUserLocation() {
        if (this.locationRequest) return this.locationRequest;
        const button = this.elements.locationBtn;
        const status = document.getElementById('geo-status');
        const report = message => { if (status) status.textContent = message; };
        if (!window.isSecureContext || !navigator.geolocation) {
            report('La ubicación requiere HTTPS o localhost.');
            return Promise.resolve(null);
        }
        if (button) button.disabled = true;
        report('Buscando tu ubicación…');
        this.locationRequest = new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, {enableHighAccuracy:false, maximumAge:60000, timeout:20000});
        }).then(position => {
            const coords = {lat:position.coords.latitude, lng:position.coords.longitude, accuracy:position.coords.accuracy};
            this.state.userLocation = coords;
            this.saveUserLocation(coords);
            report('Ubicación encontrada.');
            if (window.mapGL) window.mapGL.showPosition(coords.lat, coords.lng);
            else this.centerMap(coords.lat, coords.lng);
            return coords;
        }, error => {
            report('Ubicación no disponible.');
            return null;
        }).finally(() => {
            if (button) button.disabled = false;
            this.locationRequest = null;
        });
        return this.locationRequest;
    }
    saveUserLocation(coords) {
        try {
            localStorage.setItem('userLat', coords.lat);
            localStorage.setItem('userLng', coords.lng);
        } catch (e) { console.error(e); }
    }
    updateMapMarkers(restaurants) {
        if (typeof window.updateMarkers === 'function') window.updateMarkers(restaurants);
    }
    centerMap(lat, lng) {
        if (typeof window.centerMap === 'function') window.centerMap(lat, lng);
    }
    toggleNotifications() {
        const panel = this.elements.notificationPanel;
        if (panel) {
            const isVisible = panel.style.display === 'block';
            panel.style.display = isVisible ? 'none' : 'block';
        }
    }
    loadFavorites() {}
    async toggleFavorite(id, event) {
        if (event) event.stopPropagation();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new AppController();
});
window.toggleFavorite = function(id, event) {
    if (window.app) window.app.toggleFavorite(id, event);
};
"""

# ============================================================
# 10. ai-assistant.js
# ============================================================
FILES["ai-assistant.js"] = r"""/* AI Assistant widget. Simplified functional version. */
(function () {
    'use strict';
    const API_CHAT = '/descubrir/api/recommend';
    const getApp = () => window.app;
    const el = (tag, className, text) => {
        const n = document.createElement(tag);
        if (className) n.className = className;
        if (text != null) n.textContent = text;
        return n;
    };
    function injectStyles() {
        if (document.getElementById('ai-assistant-styles')) return;
        const s = document.createElement('style');
        s.id = 'ai-assistant-styles';
        s.textContent = `
            .ai-fab { position:fixed; right:20px; bottom:20px; z-index:1200; width:58px; height:58px; border:none; border-radius:50%; cursor:pointer; color:var(--theme-text); font-size:var(--text-xl); background:linear-gradient(135deg,var(--theme-accent-bg),var(--theme-danger-bg)); box-shadow:0 8px 22px var(--theme-shadow); transition:transform .2s ease; }
            .ai-fab:hover { transform:scale(1.08); }
            .ai-chat { position:fixed; right:20px; bottom:92px; z-index:1200; width:360px; max-width:calc(100vw - 40px); height:520px; max-height:calc(100vh - 120px); display:flex; flex-direction:column; overflow:hidden; background:var(--theme-surface); border-radius:18px; box-shadow:0 18px 50px var(--theme-shadow); }
            .ai-chat-head { display:flex; align-items:center; justify-content:space-between; padding:var(--space-md); color:var(--theme-text); font-weight:700; background:linear-gradient(135deg,var(--theme-accent-bg),var(--theme-danger-bg)); }
            .ai-chat-close { border:none; background:none; color:var(--theme-text); font-size:var(--text-xl); cursor:pointer; }
            .ai-chat-body { flex:1; overflow-y:auto; padding:var(--space-md); display:flex; flex-direction:column; gap:var(--space-sm); background:var(--theme-surface); }
            .ai-bubble { max-width:85%; padding:var(--space-sm) var(--space-md); border-radius:14px; font-size:var(--text-sm); line-height:1.45; }
            .ai-bubble.bot { align-self:flex-start; background:var(--theme-surface); color:var(--theme-text); border:1px solid var(--theme-border); }
            .ai-bubble.user { align-self:flex-end; background:var(--theme-accent-bg); color:var(--theme-text); }
            .ai-chat-form { display:flex; gap:var(--space-sm); padding:var(--space-sm); border-top:1px solid var(--theme-border); background:var(--theme-surface); }
            .ai-chat-input { flex:1; min-width:0; padding:var(--space-sm) var(--space-md); border:1px solid var(--theme-border); border-radius:999px; outline:none; font-size:var(--text-sm); }
            .ai-chat-send { width:40px; height:40px; border:none; border-radius:50%; cursor:pointer; color:var(--theme-text); background:var(--theme-accent-bg); }
        `;
        document.head.appendChild(s);
    }
    function buildChat() {
        const fab = el('button', 'ai-fab');
        fab.type = 'button';
        fab.title = 'Asistente IA';
        fab.textContent = 'IA';
        fab.setAttribute('aria-label', 'Abrir asistente IA');
        const panel = el('div', 'ai-chat');
        panel.style.display = 'none';
        panel.innerHTML = `<div class="ai-chat-head"><span>Asistente SmartResto</span><button type="button" class="ai-chat-close" aria-label="Cerrar">×</button></div><div class="ai-chat-body"></div><div class="ai-chat-form"><input type="text" class="ai-chat-input" maxlength="300" placeholder="¿Qué se te antoja?"><button type="button" class="ai-chat-send" aria-label="Enviar">↑</button></div>`;
        document.body.append(fab, panel);
        const body = panel.querySelector('.ai-chat-body');
        const input = panel.querySelector('.ai-chat-input');
        const sendBtn = panel.querySelector('.ai-chat-send');
        function addBubble(role, text) {
            const b = el('div', 'ai-bubble ' + role, text);
            body.appendChild(b);
            body.scrollTop = body.scrollHeight;
            return b;
        }
        async function send() {
            const text = input.value.trim();
            if (!text) return;
            input.value = '';
            addBubble('user', text);
            const typing = addBubble('bot', 'Pensando…');
            try {
                const response = await fetch(API_CHAT, {
                    method: 'POST',
                    headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({contexto: text, restricciones: [], preferencias: []})
                });
                const data = await response.json();
                typing.remove();
                const razon = data?.recomendacion?.razon || 'Sin recomendaciones disponibles.';
                addBubble('bot', razon);
            } catch (e) {
                typing.remove();
                addBubble('bot', 'No pude consultar la IA en este momento.');
            }
        }
        fab.addEventListener('click', () => {
            const open = panel.style.display === 'flex';
            panel.style.display = open ? 'none' : 'flex';
            if (!open) input.focus();
        });
        panel.querySelector('.ai-chat-close').addEventListener('click', () => panel.style.display = 'none');
        sendBtn.addEventListener('click', send);
        input.addEventListener('keydown', e => { if (e.key === 'Enter') send(); });
        addBubble('bot', '¡Hola! Soy tu asistente de SmartResto. Cuéntame qué se te antoja.');
    }
    function init() {
        if (document.querySelector('.ai-fab')) return;
        injectStyles();
        buildChat();
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once: true});
    else init();
})();
"""

# ============================================================
# 11. copilot-wake.js
# ============================================================
FILES["copilot-wake.js"] = r"""(() => {
  if (window.smartrestoVoice) return;
  const panel = document.getElementById('sr-wake');
  if (!panel) return;
  const toggle = document.getElementById('sr-wake-toggle');
  const enable = document.getElementById('sr-wake-enable');
  const status = document.getElementById('sr-wake-status');
  const Speech = window.SpeechRecognition || window.webkitSpeechRecognition;
  const key = 'smartresto:copilot-wake-enabled';
  let preferred = true;
  try { preferred = localStorage.getItem(key) !== 'false'; } catch (_) {}
  let authorized = false, blocked = false, running = false, disposed = false;
  let timer = null, failures = 0;
  const pending = new Map();
  function ready() {
    const callbacks = [...pending.values()]; pending.clear();
    callbacks.forEach(next => next());
  }
  const owners = new Set();
  const recognition = Speech ? new Speech() : null;
  const say = text => { if (status) status.textContent = text; };
  const eligible = () => preferred && authorized && !blocked && !disposed && !document.hidden && !owners.size;
  function stop() {
    clearTimeout(timer); timer = null;
    if (running) { try { recognition.abort(); } catch (_) {} }
  }
  function start() {
    clearTimeout(timer); timer = null;
    if (!recognition || !eligible() || running) return;
    try { running = true; say('Iniciando micrófono…'); recognition.start(); }
    catch (_) { running = false; blocked = true; say('Pulsa Habilitar micro para reintentar.'); }
  }
  function resume() {
    if (eligible() && !running) timer = setTimeout(start, 600);
  }
  window.smartrestoVoice = {
    acquire(owner, ready) {
      owners.add(owner); if (ready) pending.set(owner, ready);
      stop(); say('Activación pausada por dictado o audio.');
      if (!running) { const next = pending.get(owner); pending.delete(owner); next?.(); }
    },
    release(owner) { pending.delete(owner); owners.delete(owner); resume(); }
  };
  if (toggle) {
    toggle.checked = preferred;
    toggle.addEventListener('change', () => {
      preferred = toggle.checked;
      try { localStorage.setItem(key, String(preferred)); } catch (_) { say('Preferencia no persistida.'); }
      if (!preferred) { stop(); say('Activación por voz desactivada.'); }
      else if (authorized && !blocked) start();
      else say('Preferencia activa. Pulsa Habilitar micro.');
    });
  }
  if (enable) {
    enable.addEventListener('click', () => {
      if (!preferred) { say('Activa primero el interruptor.'); return; }
      authorized = true; blocked = false; failures = 0; start();
    });
  }
  if (!recognition) {
    if (enable) enable.disabled = true;
    say('Voz no disponible en este navegador.');
  } else {
    recognition.lang = 'es-PE'; recognition.continuous = true; recognition.interimResults = false;
    recognition.addEventListener('start', () => {
      if (!eligible()) { stop(); return; }
      say('Escuchando: hola smart copilot.');
    });
    recognition.addEventListener('result', event => {
      if (!eligible()) return;
      failures = 0;
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (!event.results[i].isFinal) continue;
        const text = event.results[i][0].transcript.trim();
        const normalized = text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
        const match = /(?:^|\s)hola[\s,]+(?:smart\s*resto\s*copilot|smart\s*copilot|copilot)(?=$|[\s,.!?])/i.exec(normalized);
        if (!match) continue;
        const transcript = text.slice(match.index + match[0].length).replace(/^[\s,.!?]+/, '').trim();
        window.smartrestoVoice.acquire('handoff', () => {
          if (disposed) return;
          if (document.getElementById('copilot-question')) {
            document.dispatchEvent(new CustomEvent('smartresto:copilot-wake', { detail: { transcript } }));
            window.smartrestoVoice.release('handoff');
          } else {
            const target = new URL(panel.dataset.copilotUrl || '/', window.location.origin);
            target.searchParams.set('voice', '1');
            if (transcript) target.searchParams.set('voice_intent', transcript.slice(0, 2000));
            window.location.assign(target.href);
          }
        });
        break;
      }
    });
    recognition.addEventListener('error', event => {
      if (event.error === 'aborted' && !eligible()) return;
      if (['not-allowed', 'service-not-allowed', 'audio-capture'].includes(event.error) || ++failures >= 3) {
        blocked = true; authorized = false; stop(); say('Micrófono detenido. Revisa permisos.');
      }
    });
    recognition.addEventListener('end', () => {
      running = false;
      if (pending.size) ready();
      else {
        if (eligible() && ++failures >= 6) { blocked = true; say('Reconexiones detenidas.'); }
        else { if (eligible()) say('Reconectando micrófono…'); resume(); }
      }
    });
    say(preferred ? 'Preferencia activa. Pulsa Habilitar micro.' : 'Activación por voz desactivada.');
  }
  document.addEventListener('visibilitychange', () => { if (document.hidden) { stop(); say('Escucha pausada.'); } else resume(); });
  window.addEventListener('pagehide', () => { disposed = true; pending.clear(); owners.clear(); stop(); });
})();
"""

# ============================================================
# 12. notification-feed.js
# ============================================================
FILES["notification-feed.js"] = r"""(() => {
  'use strict';
  const script = document.currentScript || document.querySelector('script[data-feed]');
  if (!script || window.srNotificationFeed) return;
  window.srNotificationFeed = true;
  const prefix = `sr-notifications:${script.dataset.user}:`;
  const button = document.createElement('button');
  button.type = 'button';
  button.title = 'Actualización periódica, no tiempo real estricto';
  const controls = document.getElementById('sr-audio-controls');
  if (!controls) { window.srNotificationFeed = false; return; }
  controls.append(button);
  const status = document.createElement('span');
  status.setAttribute('role', 'status');
  button.after(status);
  let context, timer, controller, stopped = false, initialized = false, enabled = false;
  let high = 0;
  const seen = new Set();
  const get = key => { try { return localStorage.getItem(prefix + key); } catch { return null; } };
  const set = (key, value) => { try { localStorage.setItem(prefix + key, value); return true; } catch { return false; } };
  let muted = get('muted') !== 'false';
  function label() {
    button.textContent = muted ? 'Activar sonidos' : enabled ? 'Silenciar sonidos' : 'Habilitar audio';
    button.setAttribute('aria-pressed', String(!muted && enabled));
  }
  label();
  button.addEventListener('click', async () => {
    if (enabled && !muted) {
      muted = true;
      set('muted', 'true');
      await context?.suspend();
    } else {
      try {
        const Audio = window.AudioContext || window.webkitAudioContext;
        if (!Audio) throw new Error('Audio unavailable');
        context ||= new Audio();
        await context.resume();
        enabled = context.state === 'running';
        muted = !enabled;
        set('muted', String(muted));
        status.textContent = enabled ? '' : 'Audio bloqueado por el navegador';
      } catch { status.textContent = 'Audio no disponible'; }
    }
    label();
  });
  function tone(n) {
    if (muted || !enabled || context?.state !== 'running') return;
    const type = n.type || 'info';
    const frequency = {order: 660, promotion: 440, message: 550, warning: 330, success: 740, info: 600}[type] || 600;
    const oscillator = context.createOscillator(), gain = context.createGain();
    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(frequency, context.currentTime);
    gain.gain.setValueAtTime(0, context.currentTime);
    gain.gain.linearRampToValueAtTime(.08, context.currentTime + .015);
    gain.gain.exponentialRampToValueAtTime(.001, context.currentTime + .22);
    oscillator.connect(gain); gain.connect(context.destination);
    oscillator.onended = () => { oscillator.disconnect(); gain.disconnect(); };
    oscillator.start(); oscillator.stop(context.currentTime + .24);
  }
  async function refresh() {
    if (stopped || document.hidden) return;
    controller = new AbortController();
    try {
      const response = await fetch(script.dataset.feed || '/api/notifications', {cache: 'no-store', signal: controller.signal});
      if (response.status === 401 || response.status === 403) { cleanup(); return; }
      if (!response.ok) throw new Error('Feed unavailable');
      const data = await response.json();
      if (stopped) return;
      const rows = data.notifications || [];
      document.querySelectorAll('[data-count="notificaciones"], #notificationBadge').forEach(node => {
        node.textContent = String(data.unread_count);
        node.hidden = data.unread_count === 0;
      });
      rows.forEach(n => { if (n.id > high && !seen.has(n.id) && !n.read) tone(n); });
      rows.forEach(n => seen.add(n.id));
      if (seen.size > 1000) seen.clear();
      high = Math.max(high, ...rows.map(n => Number(n.id)));
      initialized = true;
    } catch (error) {
      if (error.name !== 'AbortError') status.textContent = 'Notificaciones sin conexión';
    } finally {
      controller = null;
      if (!stopped) timer = setTimeout(refresh, 10000);
    }
  }
  function cleanup() {
    stopped = true;
    clearTimeout(timer);
    controller?.abort();
    context?.close();
  }
  window.addEventListener('pagehide', cleanup);
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden && !stopped && !controller) { clearTimeout(timer); refresh(); }
  });
  refresh();
})();
"""

# ============================================================
# 13. admin.js (versión funcional base)
# ============================================================
FILES["admin.js"] = r"""/**
 * SmartResto - Panel de Administración
 */
class AdminController {
    constructor() {
        this.chartInstances = {};
        this.init();
    }
    init() {
        if (document.querySelector('.charts-container')) {
            setTimeout(() => this.loadAnalytics(), 300);
        }
        this.initTable();
        this.initModals();
    }
    async requestJSON(url, method = 'GET', payload = null) {
        const opts = { method, headers: { 'Accept': 'application/json' } };
        const csrf = document.querySelector('meta[name="csrf-token"]');
        if (csrf) opts.headers['X-CSRFToken'] = csrf.content;
        if (payload) {
            opts.headers['Content-Type'] = 'application/json';
            opts.body = JSON.stringify(payload);
        }
        const res = await fetch(url, opts);
        const isJson = (res.headers.get('content-type') || '').includes('application/json');
        if (!res.ok || !isJson) {
            let msg;
            if (isJson) msg = (await res.json().catch(() => ({}))).error || `Error ${res.status}`;
            else if (res.redirected || res.status === 401 || res.status === 403) msg = 'Sesión expirada o sin permisos';
            else msg = `El servidor devolvió HTML (status ${res.status})`;
            throw new Error(msg);
        }
        return res.json();
    }
    destroyAllCharts() {
        Object.keys(this.chartInstances).forEach(key => {
            try { this.chartInstances[key].destroy(); } catch (e) {}
            delete this.chartInstances[key];
        });
        if (typeof Chart !== 'undefined' && Chart.getChart) {
            document.querySelectorAll('canvas').forEach(canvas => {
                const old = Chart.getChart(canvas);
                if (old) old.destroy();
            });
        }
    }
    async loadAnalytics() {
        try {
            this.destroyAllCharts();
            const data = await this.requestJSON('/admin/api/analytics');
            if (!data || !data.prices || !data.ratings) return;
            setTimeout(() => this.createCharts(data), 100);
        } catch (error) {
            console.error('Error cargando analytics:', error);
        }
    }
    makeChart(key, canvasId, config) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        try {
            const old = Chart.getChart ? Chart.getChart(canvas) : null;
            if (old) old.destroy();
            this.chartInstances[key] = new Chart(canvas, config);
        } catch (error) {
            console.error(`Error creando gráfico ${key}:`, error);
        }
    }
    createCharts(data) {
        const css = getComputedStyle(document.documentElement);
        const primaryColor = css.getPropertyValue('--theme-accent').trim() || '#a6dfc6';
        const secondaryColor = css.getPropertyValue('--theme-info').trim() || '#b7d8ff';
        if (data.prices && data.prices.length > 0) {
            this.makeChart('price', 'priceChart', {
                type: 'bar',
                data: {
                    labels: data.prices.map((_, i) => `Rest ${i + 1}`),
                    datasets: [{ label: 'Precio Promedio (S/.)', data: data.prices, backgroundColor: primaryColor, borderRadius: 4 }]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
            });
        }
        if (data.ratings && data.ratings.length > 0) {
            this.makeChart('rating', 'ratingChart', {
                type: 'line',
                data: {
                    labels: data.ratings.map((_, i) => `Rest ${i + 1}`),
                    datasets: [{ label: 'Rating', data: data.ratings, borderColor: secondaryColor, tension: 0.1 }]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
            });
        }
    }
    initTable() {
        const tableSearch = document.getElementById('tableSearch');
        if (tableSearch) tableSearch.addEventListener('input', (e) => this.filterTable(e.target.value));
    }
    filterTable(query) {
        const rows = document.querySelectorAll('.admin-table:not(.users-table) tbody tr');
        const q = query.toLowerCase();
        rows.forEach(row => { row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none'; });
    }
    initModals() {
        const editModal = document.getElementById('editModal');
        const closeModal = document.querySelector('.close-modal');
        const form = document.getElementById('editForm');
        if (closeModal && editModal) closeModal.addEventListener('click', () => { editModal.style.display = 'none'; });
        window.addEventListener('click', (e) => { if (editModal && e.target === editModal) editModal.style.display = 'none'; });
        document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && editModal) editModal.style.display = 'none'; });
        if (form) form.addEventListener('submit', (e) => { e.preventDefault(); this.saveRestaurant(form); });
    }
    async editRestaurant(id) {
        try {
            const data = await this.requestJSON(`/admin/restaurant/${id}`);
            const form = document.getElementById('editForm');
            if (!form) return;
            form.dataset.id = id;
            form.querySelector('input[name="name"]').value = data.name ?? '';
            form.querySelector('input[name="avg_price"]').value = data.avg_price ?? '';
            form.querySelector('input[name="rating"]').value = data.rating ?? '';
            form.querySelector('textarea[name="description"]').value = data.description ?? '';
            document.getElementById('editModal').style.display = 'block';
        } catch (error) {
            alert(error.message);
        }
    }
    async saveRestaurant(form) {
        const id = form.dataset.id;
        if (!id) return;
        const payload = {
            name: form.querySelector('input[name="name"]').value.trim(),
            avg_price: parseFloat(form.querySelector('input[name="avg_price"]').value),
            rating: parseFloat(form.querySelector('input[name="rating"]').value),
            description: form.querySelector('textarea[name="description"]').value.trim()
        };
        if (!payload.name) { alert('El nombre es obligatorio'); return; }
        try {
            await this.requestJSON(`/admin/restaurant/${id}`, 'PUT', payload);
            location.reload();
        } catch (error) {
            alert(error.message);
        }
    }
    async deleteRestaurant(id) {
        if (!confirm('¿Estás seguro de eliminar este restaurante?')) return;
        try {
            await this.requestJSON(`/admin/restaurant/${id}`, 'DELETE');
            location.reload();
        } catch (error) {
            alert(error.message);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.admin = new AdminController();
});
"""

# ============================================================
# 14. admin-dashboard.js
# ============================================================
FILES["admin-dashboard.js"] = r"""(() => {
 const canvases=document.querySelectorAll('[data-admin-chart]');
 if(!window.Chart){canvases.forEach(c=>{c.parentElement.hidden=true;c.closest('section')?.querySelector('details')?.setAttribute('open','');});return;}
 const charts=[];const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 const draw=()=>{charts.splice(0).forEach(c=>c.destroy());const css=getComputedStyle(document.body),fg=css.getPropertyValue('--sr-text').trim()||window.SRTheme.color('text'),brand=css.getPropertyValue('--sr-brand').trim()||window.SRTheme.color('success');canvases.forEach(canvas=>{const rows=JSON.parse(canvas.dataset.adminChart||'[]'),line=canvas.dataset.chartKind==='line';charts.push(new Chart(canvas,{type:line?'line':'bar',data:{labels:rows.map(x=>x[0]),datasets:[{label:'Registros',data:rows.map(x=>x[1]),borderColor:brand,backgroundColor:brand,borderWidth:2,borderRadius:6,tension:.25,pointRadius:3}]},options:{responsive:true,maintainAspectRatio:false,animation:reduced.matches?false:{duration:250},plugins:{legend:{display:false}},scales:{x:{ticks:{color:fg,maxRotation:35,autoSkip:true},grid:{display:false}},y:{beginAtZero:true,ticks:{color:fg,precision:0},grid:{color:window.SRTheme.color('text')}}}}}));});};draw();new MutationObserver(draw).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
})();
"""

# ============================================================
# 15. admin-precision.js
# ============================================================
FILES["admin-precision.js"] = r"""/* Admin precision helpers. Optional enhancements for admin UI. */
(() => {
  'use strict';
  document.addEventListener('DOMContentLoaded', () => {
    if (!document.body.classList.contains('sr-admin-precision')) return;
    document.querySelectorAll('[data-admin-confirm]').forEach(btn => {
      btn.addEventListener('click', e => {
        const msg = btn.dataset.adminConfirm || '¿Confirmar acción?';
        if (!window.confirm(msg)) e.preventDefault();
      });
    });
  });
})();
"""

# ============================================================
# 16. communication.js
# ============================================================
FILES["communication.js"] = r"""document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-mailbox]').forEach(box => {
    const items = [...box.querySelectorAll('[data-mail-item]')];
    const details = [...box.querySelectorAll('[data-mail-detail]')];
    const search = box.querySelector('[data-mail-search]');
    const filter = box.querySelector('[data-mail-filter]');
    function select(item) {
      items.forEach(row => row.setAttribute('aria-expanded', String(row === item)));
      details.forEach(detail => { detail.hidden = !item || detail.id !== item.dataset.mailItem; });
    }
    function update() {
      const query = search.value.trim().toLocaleLowerCase('es');
      items.forEach(item => { item.hidden = !item.textContent.toLocaleLowerCase('es').includes(query) || Boolean(filter?.value && filter.value !== item.dataset.state); });
      const visible = items.filter(item => !item.hidden);
      select(visible.find(item => item.getAttribute('aria-expanded') === 'true') || visible[0]);
      box.querySelector('[data-mail-status]').textContent = `${visible.length} resultados`;
    }
    items.forEach(item => item.addEventListener('click', () => select(item)));
    search.addEventListener('input', update);
    filter?.addEventListener('change', update);
    update();
  });
});
"""

# ============================================================
# 17. scan.js
# ============================================================
FILES["scan.js"] = r"""(() => {
  'use strict';
  const root = document.getElementById('smartScan');
  if (!root) return;
  const get = id => document.getElementById(id);
  const form = get('scanForm'), status = get('scanStatus'), video = get('scanVideo');
  let selected = null, stream = null, previewUrl = null, generation = 0, busy = false;
  function stopCamera() {
    generation++;
    if (stream) stream.getTracks().forEach(track => track.stop());
    stream = null; if (video) video.srcObject = null;
    const c = get('scanCamera'); if (c) c.hidden = true;
  }
  async function select(file) {
    if (!file) return;
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || !file.size || file.size > 8 * 1024 * 1024) {
      status.textContent = 'Selecciona JPEG, PNG o WebP de hasta 8 MB.'; return;
    }
    const url = URL.createObjectURL(file);
    const image = new Image();
    image.onload = () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      previewUrl = url; selected = file;
      get('scanPreview').src = url; get('scanPreview').hidden = false;
      status.textContent = `${file.name} seleccionada. Lista para analizar.`;
    };
    image.onerror = () => { URL.revokeObjectURL(url); status.textContent = 'El archivo no contiene una imagen legible.'; };
    image.src = url;
  }
  get('scanLibrary')?.addEventListener('change', event => select(event.target.files[0]));
  get('scanCapture')?.addEventListener('change', event => select(event.target.files[0]));
  const camera = get('scanOpenCamera');
  if (camera) {
    camera.hidden = false;
    camera.addEventListener('click', async () => {
      if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia) {
        status.textContent = 'La cámara del navegador requiere HTTPS y soporte getUserMedia.'; return;
      }
      stopCamera(); const current = generation;
      try {
        const acquired = await navigator.mediaDevices.getUserMedia({video: {facingMode: {ideal: 'environment'}}, audio: false});
        if (current !== generation || document.hidden) { acquired.getTracks().forEach(track => track.stop()); return; }
        stream = acquired; video.srcObject = stream; get('scanCamera').hidden = false; await video.play();
        status.textContent = 'Cámara activa. Captura cuando estés listo.';
      } catch (_) { stopCamera(); status.textContent = 'No se pudo abrir la cámara.'; }
    });
  }
  get('scanCloseCamera')?.addEventListener('click', stopCamera);
  get('scanTake')?.addEventListener('click', () => {
    if (!video.videoWidth || !video.videoHeight) { status.textContent = 'Espera a que la cámara muestre una imagen.'; return; }
    const canvas = document.createElement('canvas');
    const scale = Math.min(1, 2048 / Math.max(video.videoWidth, video.videoHeight));
    canvas.width = Math.round(video.videoWidth * scale); canvas.height = Math.round(video.videoHeight * scale);
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(blob => {
      if (blob) select(new File([blob], 'smartscan.jpg', {type: 'image/jpeg'}));
      else status.textContent = 'No se pudo capturar la foto.';
    }, 'image/jpeg', 0.9);
    stopCamera();
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) stopCamera(); });
  window.addEventListener('pagehide', stopCamera);
  if (form) form.addEventListener('submit', async event => {
    event.preventDefault();
    if (busy) return;
    if (!selected) { status.textContent = 'Selecciona una imagen legible antes de analizar.'; return; }
    const body = new FormData(form); body.set('photo', selected);
    busy = true; get('scanSubmit').disabled = true; status.textContent = 'Analizando…';
    try {
      const response = await fetch(form.action || location.href, {method: 'POST', body, credentials: 'same-origin', headers: {'Accept': 'application/json'}});
      const data = await response.json();
      if (!response.ok || data.success !== true) throw new Error(data.error || 'No se completó el análisis.');
      const result = get('scanResult');
      if (data.html && result) {
        const parsed = new DOMParser().parseFromString(data.html, 'text/html');
        result.replaceChildren(...parsed.body.childNodes);
      }
      status.textContent = 'Análisis completado.';
    } catch (error) { status.textContent = error.message; }
    finally { busy = false; get('scanSubmit').disabled = false; }
  });
})();
"""

# ============================================================
# 18. editorial-slides.js
# ============================================================
FILES["editorial-slides.js"] = r"""(() => {
 const motion = matchMedia('(prefers-reduced-motion: reduce)');
 document.querySelectorAll('[data-editorial-slides]').forEach(host => {
   let items; try { items = JSON.parse(host.dataset.editorialSlides); } catch { return; }
   items = items.filter(x => typeof x === 'string' && x.startsWith('/static/images/'));
   const photo = host.querySelector('img'), pause = host.querySelector('[data-slide-pause]');
   if (!photo || !pause) return;
   const pauseContext = (pause.getAttribute('aria-label') || 'Pausar presentación').replace(/^Pausar\s+/i, '') || 'presentación';
   const pauseLabel = pause.querySelector('[data-slide-pause-label], span');
   let index = 0, paused = motion.matches, visible = false;
   const update = () => {
     const label = paused ? 'Reanudar' : 'Pausar';
     if (pauseLabel) pauseLabel.textContent = label;
     else {
       const textNode = Array.from(pause.childNodes).find(node => node.nodeType === Node.TEXT_NODE && node.textContent.trim());
       if (textNode) textNode.textContent = label;
       else pause.append(document.createTextNode(label));
     }
     pause.setAttribute('aria-label', `${label} ${pauseContext}`);
     pause.setAttribute('aria-pressed', String(paused));
   };
   const next = () => { if (!items.length) return; index=(index+1)%items.length; photo.src=items[index]; };
   host.querySelector('[data-slide-next]')?.addEventListener('click',next);
   pause.addEventListener('click',()=>{paused=!paused;update();});
   const observer=new IntersectionObserver(([entry])=>{visible=entry.isIntersecting;}); observer.observe(host);
   const timer=setInterval(()=>{if(visible&&!paused&&!document.hidden&&!host.matches(':focus-within,:hover'))next();},9000);
   motion.addEventListener('change',()=>{paused=motion.matches;update();});update();
   window.addEventListener('pagehide',()=>{clearInterval(timer);observer.disconnect();},{once:true});
 });
})();
"""

# ============================================================
# 19. theme-charts.js
# ============================================================
FILES["theme-charts.js"] = r"""(() => {
  if (!window.Chart) return;
  Chart.register({id:'srTheme', beforeUpdate(chart) {
    const c = window.SRTheme.color;
    chart.options.color = c('text');
    if (chart.options.plugins.legend) chart.options.plugins.legend.labels.color = c('text');
    if (chart.options.plugins.tooltip) Object.assign(chart.options.plugins.tooltip, {backgroundColor:c('elevated'), titleColor:c('text'), bodyColor:c('text'), borderColor:c('border'), borderWidth:1});
    Object.values(chart.options.scales || {}).forEach(scale => {
      if (scale.ticks) scale.ticks.color = c('muted');
      if (scale.grid) scale.grid.color = c('border');
      if (scale.title) scale.title.color = c('text');
    });
    chart.data.datasets.forEach((dataset, index) => {
      const multi = ['pie','doughnut','polarArea'].includes(chart.config.type);
      dataset.backgroundColor = multi ? chart.data.labels.map((_, i) => c('chart-' + (i % 6 + 1))) : c('chart-' + (index % 6 + 1));
      dataset.borderColor = multi ? c('surface') : c('chart-' + (index % 6 + 1));
    });
  }});
  document.addEventListener('themechange', () => Object.values(Chart.instances).forEach(chart => chart.update('none')));
})();
"""

# ============================================================
# 20. dish-model.js
# ============================================================
FILES["dish-model.js"] = r"""(() => {
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
"""

# ============================================================
# 21. catalog-explore.js
# ============================================================
FILES["catalog-explore.js"] = r"""(() => {
    const form = document.getElementById('catalog-search');
    if (!form) return;
    const status = document.getElementById('catalog-status');
    const results = document.getElementById('catalog-results');
    if (!status || !results) return;
    const origin = {};
    const selected = new Set();
    const products = new Set();
    const declaration = value => Array.isArray(value) ? value.join(', ') || 'Ninguno declarado' : 'Sin declarar';
    const text = (parent, tag, value) => {
        const node = document.createElement(tag); node.textContent = value; parent.append(node); return node;
    };
    async function api(url, body) {
        const token = document.querySelector('meta[name="csrf-token"]')?.content;
        const response = await fetch(url, body ? {method:'POST', headers:{'Content-Type':'application/json', 'X-CSRFToken':token || ''}, body:JSON.stringify(body)} : {});
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'No se pudo consultar el catálogo');
        return data;
    }
    form.onsubmit = async event => {
        event.preventDefault();
        const filters = {...origin};
        for(const input of form.elements) if(input.name && input.value && (input.type !== 'checkbox' || input.checked)) filters[input.name]=input.type==='checkbox' ? true : input.value;
        try {
            const data = await api('/descubrir/api/restaurants', filters);
            results.replaceChildren();
            const rows = Array.isArray(data) ? data : (data.results || []);
            status.textContent = `${rows.length} negocios encontrados`;
            rows.forEach(row => {
                const card = document.createElement('article');
                card.style.padding = '16px';
                results.append(card);
                text(card, 'h2', row.nombre || row.name || 'Sin nombre');
                text(card, 'p', `${row.distrito || row.district || ''} | S/ ${row.precio_promedio || row.avg_price || 0}`);
                const link = text(card, 'a', 'Ver negocio');
                link.href = `/negocio/${row.id_restaurante || row.id}`;
            });
        } catch (error) { status.textContent = error.message; }
    };
})();
"""

# ============================================================
# 22. recommendations.js
# ============================================================
FILES["recommendations.js"] = r"""(() => {
  'use strict';
  const page = document.querySelector('[data-recommendations]');
  if (!page) return;
  async function post(url, payload, keepalive = false) {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      keepalive,
    });
    const result = await response.json();
    if (!response.ok || !result.success) throw new Error(result.error || 'No se pudo guardar el cambio.');
    return result;
  }
  const cards = new Map();
  for (const card of page.querySelectorAll('[data-rec-card][data-token]')) {
    const entry = {
      card,
      list: card.closest('[data-rec-list]'),
      like: card.querySelector('[data-rec-like]'),
      dismiss: card.querySelector('[data-rec-dismiss]'),
      undo: card.querySelector('[data-rec-undo]'),
      body: card.querySelector('.rec-card-main'),
      dismissed: card.querySelector('[data-rec-dismissed]'),
    };
    const key = card.dataset.recKey;
    if (!cards.has(key)) cards.set(key, []);
    cards.get(key).push(entry);
    entry.like?.addEventListener('click', () => saveFeedback(entry, entry.like.getAttribute('aria-pressed') === 'true' ? 'undo' : 'like', entry.like));
    entry.dismiss?.addEventListener('click', () => saveFeedback(entry, 'dismiss', entry.dismiss));
    entry.undo?.addEventListener('click', () => saveFeedback(entry, 'undo', entry.undo));
  }
  async function saveFeedback(entry, action, button) {
    if (!entry.card || !page.dataset.interactionUrl) return;
    try {
      const result = await post(page.dataset.interactionUrl, { token: entry.card.dataset.token, action });
      const status = entry.list?.querySelector('[data-rec-feedback]');
      if (status) status.textContent = 'Guardado.';
    } catch (error) {
      const status = entry.list?.querySelector('[data-rec-feedback]');
      if (status) status.textContent = error.message;
    }
  }
})();
"""

# ============================================================
# 23. search-history.js
# ============================================================
FILES["search-history.js"] = r"""(() => {
  'use strict';
  const url = document.currentScript?.dataset.historyUrl;
  if (!url) return;
  const clean = value => typeof value === 'string' ? value.trim().replace(/\s+/g, ' ') : '';
  async function record(value) {
    const query = Array.from(clean(value)).slice(0, 140).join('');
    if (!query) return false;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 12000);
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, submission_id: window.crypto?.randomUUID?.() }),
        keepalive: true,
        signal: controller.signal,
      });
      return response.ok;
    } catch { return false; }
    finally { clearTimeout(timeout); }
  }
  window.smartRestoSearchHistory = { record };
  document.addEventListener('submit', event => {
    if (!(event.target instanceof HTMLFormElement)) return;
    const field = event.target.querySelector('[data-search-history]');
    if (!field || field.disabled) return;
    void record(field.value);
  }, true);
})();
"""

# ============================================================
# 24. auth.js
# ============================================================
FILES["auth.js"] = r"""/* SmartResto · Experiencia de autenticación */
(() => {
  const stage = document.getElementById('ax-stage');
  if (!stage) return;
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const DURATION = 820;
  const panes = { login: stage.querySelector('[data-pane="login"]'), register: stage.querySelector('[data-pane="register"]') };
  const titles = { login: 'Iniciar sesión · SmartResto', register: 'Crear cuenta · SmartResto' };
  let locked = false;
  function applyMode(mode) {
    stage.dataset.mode = mode;
    for (const [name, pane] of Object.entries(panes)) {
      if (!pane) continue;
      const active = name === mode;
      pane.toggleAttribute('inert', !active);
      pane.setAttribute('aria-hidden', String(!active));
    }
    document.title = titles[mode];
  }
  stage.querySelectorAll('[data-ax-switch]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.button !== 0) return;
    });
  });
  window.addEventListener('popstate', () => {
    const mode = location.pathname.replace(/\/+$/, '').endsWith('/register') ? 'register' : 'login';
    locked = false;
    applyMode(mode);
  });
  applyMode(stage.dataset.mode === 'register' ? 'register' : 'login');
  stage.querySelectorAll('[data-toggle-password]').forEach(button => {
    button.addEventListener('click', () => {
      const input = document.getElementById(button.dataset.togglePassword);
      if (!input) return;
      const show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      button.setAttribute('aria-pressed', String(show));
      button.setAttribute('aria-label', show ? 'Ocultar contraseña' : 'Mostrar contraseña');
      button.querySelector('[data-eye-open]')?.toggleAttribute('hidden', show);
      button.querySelector('[data-eye-closed]')?.toggleAttribute('hidden', !show);
      input.focus({ preventScroll: true });
    });
  });
  const messages = {
    'ax-login-username': 'Ingresa tu usuario o correo.',
    'ax-login-password': 'Ingresa tu contraseña.',
    'ax-reg-name': 'Ingresa tu nombre completo.',
    'ax-reg-username': 'Usa de 3 a 80 caracteres.',
    'ax-reg-email': 'Ingresa un correo válido.',
    'ax-reg-password': 'Mínimo 8 caracteres con letras y números.',
    'ax-reg-confirm': 'Las contraseñas no coinciden.'
  };
  function errorNode(input) { return stage.querySelector(`[data-error-for="${input.id}"]`); }
  function customError(input) {
    const value = input.value;
    switch (input.id) {
      case 'ax-reg-username': return value && !/^[a-zA-Z0-9_]{3,80}$/.test(value) ? messages[input.id] : '';
      case 'ax-reg-email': return value && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(value) ? messages[input.id] : '';
      case 'ax-reg-password': return value && !(value.length >= 8 && /[a-zA-Z]/.test(value) && /\d/.test(value)) ? messages[input.id] : '';
      case 'ax-reg-confirm': {
        const password = document.getElementById('ax-reg-password');
        return value && value !== password.value ? messages[input.id] : '';
      }
      default: return '';
    }
  }
  function paint(input, message) {
    const node = errorNode(input);
    if (node) { node.textContent = message; node.hidden = !message; }
    if (message) input.setAttribute('aria-invalid', 'true');
    else input.removeAttribute('aria-invalid');
  }
  function validate(input, reportEmpty) {
    let message = customError(input);
    if (!message && reportEmpty && input.required && !input.value.trim()) message = messages[input.id] || 'Este campo es obligatorio.';
    paint(input, message);
    return !message;
  }
  const fields = [...stage.querySelectorAll('.ax-form input:not([type="hidden"])')];
  fields.forEach(input => {
    input.addEventListener('blur', () => { if (input.value || input.dataset.touched) { input.dataset.touched = '1'; validate(input, true); } });
    input.addEventListener('input', () => { if (input.dataset.touched) validate(input, false); });
  });
  stage.querySelectorAll('.ax-form').forEach(form => {
    form.addEventListener('submit', event => {
      const inputs = [...form.querySelectorAll('input:not([type="hidden"])')];
      let firstInvalid = null;
      inputs.forEach(input => {
        input.dataset.touched = '1';
        if (!validate(input, true) && !firstInvalid) firstInvalid = input;
      });
      if (firstInvalid) { event.preventDefault(); firstInvalid.focus(); return; }
      const button = form.querySelector('.ax-submit');
      if (button?.disabled) { event.preventDefault(); return; }
      button?.classList.add('is-loading');
      button?.setAttribute('aria-busy', 'true');
      setTimeout(() => { if (button) button.disabled = true; }, 0);
    });
  });
})();
"""

# ============================================================
# 25. business-plans.js
# ============================================================
FILES["business-plans.js"] = r"""(() => {
 const root = document.querySelector('.bp-page'); if (!root) return;
 root.querySelectorAll('[data-billing]').forEach(button => button.addEventListener('click', () => {
   const annual = button.dataset.billing === 'annual';
   root.querySelectorAll('[data-billing]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
   root.querySelectorAll('[data-price]').forEach(el => el.textContent = 'S/ ' + Number(el.dataset[annual ? 'annual' : 'monthly']).toLocaleString('en-US'));
   root.querySelectorAll('[data-period]').forEach(el => el.textContent = annual ? '/ año' : '/ mes');
 }));
})();
"""

# ============================================================
# 26. business-share.js
# ============================================================
FILES["business-share.js"] = r"""const shareButton = document.getElementById("mgr-share");
shareButton?.addEventListener("click", async () => {
    const url = new URL(shareButton.dataset.public, location.origin).href;
    const status = document.getElementById("mgr-copy-status");
    try {
        if (navigator.share) {
            await navigator.share({url, title: document.title});
        } else {
            await navigator.clipboard.writeText(url);
            if (status) status.textContent = "Enlace copiado.";
        }
    } catch (error) {
        if (error.name !== "AbortError" && status) status.textContent = url;
    }
});
"""

# ============================================================
# 27. context-location.js
# ============================================================
FILES["context-location.js"] = r"""(() => {
 const button=document.getElementById('context-location');
 const status=document.getElementById('context-location-status');
 button?.addEventListener('click',()=>{
  if(!navigator.geolocation){if(status)status.textContent='Tu navegador no admite ubicación.';return;}
  button.disabled=true;if(status)status.textContent='Buscando ubicación…';
  navigator.geolocation.getCurrentPosition(async ({coords})=>{
   try {
    const response=await fetch('/api/save-location',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({lat:coords.latitude,lng:coords.longitude})});
    if(!response.ok) throw new Error();
    location.reload();
   }catch{if(status)status.textContent='No se pudo guardar la ubicación.';button.disabled=false;}
  },()=>{if(status)status.textContent='Activa el permiso de ubicación.';button.disabled=false;},{timeout:20000,maximumAge:60000});
 });
})();
"""

# ============================================================
# 28. discovery.js
# ============================================================
FILES["discovery.js"] = r"""/* Radar SmartResto. */
(function () {
  'use strict';
  const status = document.getElementById('radarStatus');
  function message(text, error) { if (!status) return; status.hidden = false; status.classList.toggle('error', !!error); status.textContent = text; }
  async function api(path, data, method = 'POST') {
    const response = await fetch(path, { method, headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) });
    const result = await response.json();
    if (!response.ok || !result.success) throw new Error(result.error || 'La operación no se completó.');
    return result;
  }
  async function busy(button, action) {
    button.disabled = true; button.setAttribute('aria-busy','true');
    try { await action(); } catch(error) { message(error.message, true); }
    finally { button.disabled = false; button.removeAttribute('aria-busy'); }
  }
  const root = document.getElementById('radarApp');
  let decision = null;
  if (root) {
    const cards = Array.from(root.querySelectorAll('.radar-candidate'));
    const search = document.getElementById('radarSearch'), filter = document.getElementById('radarFilter');
    if (search && filter) {
      function applyFilters() {
        let count = 0;
        cards.forEach(card => {
          card.hidden = !!((filter.value && card.dataset.state !== filter.value) || !card.dataset.search.includes(search.value.toLowerCase()));
          if (!card.hidden) count++;
        });
        const noMatches = document.getElementById('radarNoMatches');
        if (noMatches) noMatches.hidden = count > 0 || !cards.length;
      }
      search.addEventListener('input', applyFilters);
      filter.addEventListener('change', applyFilters);
    }
    root.addEventListener('click', event => {
      const button = event.target.closest('button[data-action]'); if (!button) return;
      if (button.dataset.action === 'scan') busy(button, async () => {
        message('Consultando…');
        const result = await api('/admin/api/discovery/runs', {source:button.dataset.source});
        message(`Corrida completada.`);
        location.reload();
      });
    });
  }
})();
"""

# ============================================================
# 29. controller.js
# ============================================================
FILES["controller.js"] = r"""/* Coordinación de eventos del home editorial. */
(() => {
  'use strict';
  document.addEventListener('DOMContentLoaded', () => {
    if (!document.body.classList.contains('sr-discover')) return;
    const byId = id => document.getElementById(id);
    const themeButton = byId('themeToggle');
    if (themeButton) {
      const themeParent = themeButton.parentElement, themeNext = themeButton.nextSibling;
      const narrowHeader = matchMedia('(max-width: 380px)');
      const placeTheme = () => {
        themeButton.classList.toggle('forest-drawer-theme', narrowHeader.matches);
        const nav = byId('sr-navigation');
        if (narrowHeader.matches && nav) nav.appendChild(themeButton);
        else themeParent.insertBefore(themeButton, themeNext?.parentNode === themeParent ? themeNext : null);
      };
      narrowHeader.addEventListener('change', placeTheme);
      placeTheme();
    }
    const form = byId('search-form');
    const reset = byId('forest-all');
    if (reset && form) {
      reset.addEventListener('click', () => {
        form.reset();
        document.querySelectorAll('.filter-chip').forEach(chip => {
          const active = chip.dataset.filter === 'all';
          chip.classList.toggle('active', active);
          chip.setAttribute('aria-pressed', String(active));
        });
        if (window.app) {
          window.app.state.filteredRestaurants = [...window.app.state.restaurants];
          window.app.renderRestaurants();
          window.app.updateMapMarkers(window.app.state.filteredRestaurants);
        }
      });
    }
  });
})();
"""

# ============================================================
# 30. logic-rules.js
# ============================================================
FILES["logic-rules.js"] = r"""/* Reglas explícitas e independientes del DOM. */
(() => {
  'use strict';
  window.ForestRules = Object.freeze({
    openingState(restaurant, now = new Date()) {
      const valid = /^([01]\d|2[0-3]):[0-5]\d$/;
      const start = restaurant.open_time, end = restaurant.close_time;
      if (!valid.test(start || '') || !valid.test(end || '')) return null;
      const time = new Intl.DateTimeFormat('en-GB', {timeZone:'America/Lima', hour:'2-digit', minute:'2-digit', hourCycle:'h23'}).format(now);
      const open = start <= end ? time >= start && time <= end : time >= start || time <= end;
      return open ? {label:'Abierto', className:'is-open'} : {label:'Cerrado', className:'is-closed'};
    }
  });
})();
"""

# ============================================================
# 31. processor.js
# ============================================================
FILES["processor.js"] = r"""/* Procesamiento puro de presentación. */
(() => {
  'use strict';
  const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const number = value => value !== null && value !== '' && Number.isFinite(Number(value)) ? Number(value) : null;
  window.ForestProcessor = Object.freeze({
    escape, number,
    tags: tags => Array.isArray(tags) ? tags.slice(0, 2) : [],
    image: value => typeof value === 'string' && (/^https?:\/\//i.test(value) || /^\/(?!\/)/.test(value)) ? value : '',
    rating: value => { const n = number(value); return n !== null && n > 0 ? n.toFixed(1) : 'Sin reseñas'; }
  });
})();
"""

# ============================================================
# 32. ui.js
# ============================================================
FILES["ui.js"] = r"""/* Render UI. */
(() => {
  'use strict';
  window.ForestUI = Object.freeze({
    renderRestaurantCard(r, favorites = [], currency = 'S/') {
      const id = Number(r.id);
      if (!Number.isSafeInteger(id) || id <= 0) return '';
      const p = window.ForestProcessor, e = p.escape;
      const image = p.image(r.image);
      const favorite = favorites.some(value => String(value) === String(id));
      const state = window.ForestRules.openingState(r);
      const reviews = p.number(r.review_count ?? r.reviews_count ?? r.num_reviews);
      const price = p.number(r.avg_price);
      return `<article class="restaurant-card rc forest-card" data-id="${id}" data-lat="${e(r.lat)}" data-lng="${e(r.lng)}">
        <div class="card-image">${image ? `<img src="${e(image)}" alt="${e(r.name)}" loading="lazy" width="640" height="480">` : `<div class="forest-photo-missing"><i class="fas fa-utensils" aria-hidden="true"></i><span>Conoce ${e(r.name)}</span></div>`}
          ${r.promo ? '<span class="forest-promo-badge"><i class="fas fa-tag" aria-hidden="true"></i> Promoción</span>' : ''}
          <button type="button" class="fav-btn" onclick="toggleFavorite(${id}, event)" aria-label="${favorite ? 'Quitar' : 'Guardar'} ${e(r.name)} ${favorite ? 'de' : 'en'} favoritos" aria-pressed="${favorite}"><i class="${favorite ? 'fas' : 'far'} fa-heart" aria-hidden="true"></i></button>
        </div><div class="card-content"><h3>${e(r.name)}</h3>
        <div class="card-location"><i class="fas fa-location-dot" aria-hidden="true"></i><span>${e(r.district || 'Ubicación por confirmar')}</span>${p.number(r.distance_km) !== null ? `<small> · ${Number(r.distance_km).toFixed(1)} km</small>` : ''}</div>
        <div class="forest-card-meta"><span class="rating"><i class="fas fa-star" aria-hidden="true"></i> ${p.rating(r.rating)}${reviews > 0 ? `<small> (${reviews} reseñas)</small>` : ''}</span>${state ? `<span class="forest-status ${state.className}">${state.label}</span>` : '<span class="forest-hours">Consultar horario</span>'}</div>
        <p class="card-price"><strong>${price !== null ? e(currency) + ' ' + price.toFixed(0) : 'Consultar precio'}</strong>${price !== null ? ' por persona' : ''}</p>
        <div class="forest-card-bottom"><div class="card-tags">${p.tags(r.tags).map(tag => `<span class="tag">${e(tag)}</span>`).join('')}</div><a href="/negocio/${id}" class="card-link">Ver restaurante <span aria-hidden="true">→</span></a></div></div></article>`;
    }
  });
})();
"""

# ============================================================
# 33. food-scene-loader.js
# ============================================================
FILES["food-scene-loader.js"] = r"""(() => {
  const loader = document.currentScript;
  const moduleUrl = loader?.dataset.sceneModule;
  const host = document.querySelector('.ax-food-host[data-food-experience-api]');
  if (!host || !moduleUrl) return;
  const desktop = window.matchMedia('(min-width: 901px)');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection || {};
  const slowNetwork = /(?:slow-)?2g/i.test(connection.effectiveType || '');
  const allowed = () => desktop.matches && !reducedMotion.matches && !connection.saveData && !slowNetwork;
  if (!allowed()) {
    host.dataset.sceneState = 'fallback';
    return;
  }
  let started = false;
  const loadScene = () => {
    if (started || !allowed() || document.hidden) return;
    started = true;
    const module = document.createElement('script');
    module.type = 'module';
    module.src = moduleUrl;
    module.onerror = () => { host.dataset.sceneState = 'fallback'; };
    document.body.append(module);
  };
  const scheduleWhenIdle = () => {
    if (!allowed()) return;
    if (document.hidden) { document.addEventListener('visibilitychange', scheduleWhenIdle, { once: true }); return; }
    window.setTimeout(() => {
      if ('requestIdleCallback' in window) window.requestIdleCallback(loadScene, { timeout: 2400 });
      else window.setTimeout(loadScene, 900);
    }, 500);
  };
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting)) { observer.disconnect(); scheduleWhenIdle(); }
    }, { rootMargin: '40px' });
    observer.observe(host);
  } else scheduleWhenIdle();
})();
"""

# ============================================================
# 34. market-map.js
# ============================================================
FILES["market-map.js"] = r"""(() => {
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
"""

# ============================================================
# 35. copilot.js
# ============================================================
FILES["copilot.js"] = r"""/* Copilot interactivo (base funcional). */
(() => {
  const form = document.getElementById('copilot-question');
  if (!form) return;
  const status = document.getElementById('copilot-status');
  const conversation = document.getElementById('copilot-conversation');
  const input = document.getElementById('copilot-message');
  const show = text => { if (status) status.textContent = text; };
  let busy = false;
  function turn(role, text) {
    if (!conversation) return;
    const article = document.createElement('article');
    article.className = 'copilot-turn ' + role;
    const label = document.createElement('strong'); label.textContent = role === 'user' ? 'Tú' : 'SmartResto Copilot';
    const p = document.createElement('p'); p.textContent = text;
    article.append(label, p);
    conversation.hidden = false;
    conversation.append(article);
    conversation.scrollTop = conversation.scrollHeight;
  }
  form.addEventListener('submit', async e => {
    e.preventDefault(); if (busy) return;
    const message = input.value.trim(); if (!message) return;
    busy = true; show('Consultando…');
    turn('user', message);
    try {
      const response = await fetch('/descubrir/api/recommend', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({contexto: message, restricciones: [], preferencias: []})
      });
      const result = await response.json();
      const reply = result?.recomendacion?.razon || 'Sin respuesta.';
      turn('assistant', reply);
      input.value = '';
      show('Listo.');
    } catch (err) {
      show('Error al consultar.');
    } finally {
      busy = false;
    }
  });
})();
"""

# ============================================================
# 36. copilot-wake.css ya lo tienes. skip
# 37. Nota: food-scene.js es bundle Three.js, no lo incluimos aquí.
# ============================================================

# ============================================================
# Copiar todos
# ============================================================
def main():
    print(f"📁 Instalando JS en: {JS_DIR}\n")
    for name, content in FILES.items():
        path = JS_DIR / name
        path.write_text(content, encoding="utf-8")
        size = len(content)
        print(f"✅ {name:<32} ({size:,} bytes)")
    print(f"\n🎉 {len(FILES)} archivos JS instalados en {JS_DIR}")
    print()
    print("⚠️  NOTA: food-scene.js (bundle Three.js ~1 MB) NO está incluido.")
    print("   Si lo necesitas para la escena 3D de auth, cópialo manualmente")
    print("   desde el proyecto viejo a app/static/js/food-scene.js.")

if __name__ == "__main__":
    main()