class AppController {
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
        try {
        const savedLat = localStorage.getItem('userLat');
        const savedLng = localStorage.getItem('userLng');
        if (savedLat && savedLng) {
            this.state.userLocation = { lat: parseFloat(savedLat), lng: parseFloat(savedLng) };
        }
        } catch (_) { /* Storage may be blocked; browsing still works. */ }
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
            this.state.restaurants = RESTAURANTS_DATA.map(r => window.ForestProcessor?.restaurant(r) || r);
            this.state.filteredRestaurants = this.state.restaurants;
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
