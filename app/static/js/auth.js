/* SmartResto · Experiencia de autenticación */
(() => {
  const stage = document.getElementById('ax-stage');
  if (!stage) return;
  const panes = { login: stage.querySelector('[data-pane="login"]'), register: stage.querySelector('[data-pane="register"]') };
  const titles = { login: 'Iniciar sesión · SmartResto', register: 'Crear cuenta · SmartResto' };
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
  window.addEventListener('popstate', () => {
    const mode = location.pathname.replace(/\/+$/, '').endsWith('/register') ? 'register' : 'login';
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
