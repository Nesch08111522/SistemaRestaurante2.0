/* Coordinación de eventos del home editorial. */
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
