/**
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
        const district = document.getElementById('district-select')?.value || document.getElementById('forest-district')?.value || '';
        const category = document.getElementById('category-select')?.value || '';
        const maxPrice = document.querySelector('input[name="max_price"]')?.value || '';
        const query = formData.get('q') || '';
        const filters = new URLSearchParams({q: query, distrito: district, categoria: category, max_price: maxPrice});
        this.showLoading();
        try {
            const response = await fetch('/descubrir/api/restaurants?' + filters, {
                signal: controller.signal
            });
            if (!response.ok) throw new Error("search");
            const data = await response.json();
            if (controller.signal.aborted) return;
            const results = Array.isArray(data) ? data : (Array.isArray(data.restaurantes) ? data.restaurantes : []);
            const normalized = results.map(r => window.ForestProcessor?.restaurant(r) || r);
            this.updateResults(normalized);
            this.updateMapMarkers(normalized);
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
