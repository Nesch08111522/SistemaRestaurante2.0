/* Theme toggle: persiste en localStorage; oscuro por defecto. */
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
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
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
