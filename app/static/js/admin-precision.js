/* Admin precision helpers. Optional enhancements for admin UI. */
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
