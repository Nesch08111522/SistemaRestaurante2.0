/* Pure presentation processing; no DOM, state or network access. */
(() => {
  'use strict';
  const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const number = value => value !== null && value !== '' && Number.isFinite(Number(value)) ? Number(value) : null;
  window.ForestProcessor = Object.freeze({escape, number,
    restaurant: r => ({...r,
      id: r.id ?? r.id_restaurante, name: r.name ?? r.nombre,
      description: r.description ?? r.descripcion, category_id: r.category_id ?? r.id_categoria,
      district: r.district ?? r.distrito, image: r.image ?? r.url_imagen,
      lat: r.lat ?? r.latitud, lng: r.lng ?? r.longitud,
      rating: r.rating ?? r.calificacion, avg_price: r.avg_price ?? r.precio_promedio,
      review_count: r.review_count ?? r.cantidad_resenas_reportada,
      promo: r.promo ?? r.promocion_texto
    }),
    tags: tags => Array.isArray(tags) ? tags.slice(0, 2) : [],
    image: value => typeof value === 'string' && (/^https?:\/\//i.test(value) || /^\/(?!\/)/.test(value)) ? value : '',
    rating: value => { const n = number(value); return n !== null && n > 0 ? n.toFixed(1) : 'Sin reseñas'; }
  });
})();
