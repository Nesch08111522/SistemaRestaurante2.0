(() => {
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
