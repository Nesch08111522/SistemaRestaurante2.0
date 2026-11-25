/**
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
