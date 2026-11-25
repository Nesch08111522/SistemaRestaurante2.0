"""
Instala los templates de SmartResto (base + auth + home).
Ejecutar: python scripts\\instalar_templates.py
"""
from pathlib import Path

TPL_DIR = Path(__file__).parent.parent / "app" / "templates"
(TPL_DIR / "partials").mkdir(parents=True, exist_ok=True)
(TPL_DIR / "auth").mkdir(parents=True, exist_ok=True)
(TPL_DIR / "public" / "partials").mkdir(parents=True, exist_ok=True)

FILES = {}

# ============================================================
# 1. base.html
# ============================================================
FILES["base.html"] = r"""{%- set shell_user = session.get('user') -%}
{%- set sr_authenticated = session.get('user_id') is not none -%}
{%- set sr_private = sr_authenticated and request.blueprint in ('owner', 'admin', 'salon', 'kitchen', 'copilot', 'intelligence', 'loyalty', 'comunicacion', 'catalog', 'sites', 'trust_center', 'companies', 'business_access') -%}
{%- set sr_auth = request.blueprint == 'auth' -%}
{%- set sr_discover = request.endpoint == 'public.home' -%}
{%- set sr_admin_ui = sr_private and shell_user is mapping and shell_user.get('role') == 'admin' -%}
{%- set sr_workspace = sr_private -%}
{%- set sr_saas_private = sr_private -%}
<!DOCTYPE html>
<html lang="es" class="sr-compact" data-theme="dark">
<head>
  <meta charset="UTF-8" />
  {% include 'partials/theme_head.html' %}
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="csrf-token" content="{{ csrf_token() }}" />
  <title>{% block title %}{{ APP_NAME }} - Recomendación Inteligente de Restaurantes{% endblock %}</title>

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Serif+Text&family=Lora:wght@400;500;600&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet" media="print" onload="this.media='all'" />

  {% if not sr_auth %}
  <link rel="stylesheet" href="{{ url_for('static', filename='vendor/material-icons/material-icons.css') }}" />
  <link rel="stylesheet" href="{{ url_for('static', filename='vendor/fontawesome/css/all.min.css') }}" />
  <link rel="stylesheet" href="{{ url_for('static', filename='vendor/leaflet/leaflet.css') }}" />
  {% endif %}

  <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}" />
  <link rel="stylesheet" href="{{ url_for('static', filename='css/components.css') }}" />
  <link rel="stylesheet" href="{{ url_for('static', filename='css/shell.css') }}" />
  <link rel="stylesheet" href="{{ url_for('static', filename='css/interface.css') }}" />
  <link rel="stylesheet" href="{{ url_for('static', filename='css/premium-system.css') }}" />
  <link rel="stylesheet" href="{{ url_for('static', filename='css/forest-depth.css') }}" />
  <link rel="stylesheet" href="{{ url_for('static', filename='css/adaptive-experience.css') }}" />
  <link rel="stylesheet" href="{{ url_for('static', filename='css/public-navigation.css') }}" />
  <link rel="stylesheet" href="{{ url_for('static', filename='css/theme-components.css') }}" />
  <link rel="stylesheet" href="{{ url_for('static', filename='css/responsive-layout.css') }}" />
  <link rel="stylesheet" href="{{ url_for('static', filename='css/layout-system.css') }}" />

  {% if sr_auth %}<link rel="stylesheet" href="{{ url_for('static', filename='css/auth.css') }}" />{% endif %}
  {% if sr_discover %}<link rel="stylesheet" href="{{ url_for('static', filename='css/forest-home.css') }}" />{% endif %}
  {% if sr_saas_private %}<link rel="stylesheet" href="{{ url_for('static', filename='css/saas-private.css') }}" />{% endif %}
  {% if sr_workspace %}<link rel="stylesheet" href="{{ url_for('static', filename='css/internal-workspace.css') }}" />{% endif %}
  {% if sr_admin_ui %}<link rel="stylesheet" href="{{ url_for('static', filename='css/admin-precision.css') }}" />{% endif %}

  {% block head %}{% endblock %}
</head>
<body data-role="{{ shell_user.get('role') if sr_authenticated else 'guest' }}"
      class="{{ 'sr-admin-precision' if sr_admin_ui else '' }} {{ 'sr-private' if sr_private else 'sr-public-site' }} {{ 'sr-workspace' if sr_workspace else '' }} {{ 'sr-saas-private' if sr_saas_private else '' }} {{ 'sr-discover' if sr_discover else '' }} {{ 'sr-auth' if sr_auth else '' }} {% block body_class %}{% endblock %}">

  <a class="skip-link" href="#main-content">Saltar al contenido principal</a>

  {% if sr_auth %}
  <a class="sr-auth-home-link" href="{{ url_for('public.home') }}" aria-label="Volver al inicio">
    <svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none"
         stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <path d="M19 12H5M12 19l-7-7 7-7"/>
    </svg>
    <span>Volver al inicio</span>
  </a>
  {% else %}
  {% include 'partials/header.html' %}
  {% endif %}

  <main id="main-content" class="main-content" tabindex="-1">
    {% include 'partials/flash.html' %}
    {% if sr_workspace %}{% include 'partials/internal_workspace_header.html' %}{% endif %}
    {% block content %}{% endblock %}
  </main>

  {% if not sr_auth and show_public_footer is not defined or show_public_footer %}
  {% include 'partials/footer.html' %}
  {% endif %}
  {% if not sr_private %}{% include 'partials/mobile_navigation.html' %}{% endif %}

  <script defer src="{{ url_for('static', filename='js/shell.js') }}"></script>
  {% if sr_private %}<script defer src="{{ url_for('static', filename='js/private-shell.js') }}"></script>{% endif %}
  <script defer src="{{ url_for('static', filename='js/security.js') }}"></script>
  <script defer src="{{ url_for('static', filename='js/responsive-layout.js') }}"></script>
  <script defer src="{{ url_for('static', filename='js/layout-system.js') }}"></script>

  {% if not sr_auth %}
  <script defer src="{{ url_for('static', filename='vendor/leaflet/leaflet.js') }}"></script>
  <script defer src="{{ url_for('static', filename='vendor/chartjs/chart-4.3.0.umd.min.js') }}"></script>
  <script defer src="{{ url_for('static', filename='js/theme-charts.js') }}"></script>
  {% endif %}

  {% block scripts %}{% endblock %}
</body>
</html>
"""

# ============================================================
# 2. 500.html
# ============================================================
FILES["500.html"] = r"""<!DOCTYPE html>
<html lang="es" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Error {{ status }} · SmartResto</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/theme-tokens.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/shell.css') }}">
  <style>
    body { display: grid; place-items: center; min-height: 100vh; margin: 0; padding: 24px; }
    .error-card { max-width: 480px; width: 100%; padding: 32px; text-align: center; background: var(--theme-surface); color: var(--theme-text); border: 1px solid var(--theme-border); border-radius: 18px; box-shadow: 0 12px 32px rgba(0,0,0,.15); }
    .error-card h1 { font-size: 48px; margin: 0 0 8px; color: var(--theme-warning); font-weight: 700; }
    .error-card p { margin: 0 0 24px; line-height: 1.55; color: var(--theme-muted); }
    .error-card a { display: inline-flex; padding: 12px 24px; border-radius: 100px; background: var(--theme-accent-bg); color: var(--theme-text); text-decoration: none; font-weight: 600; }
    .error-card a:hover { filter: brightness(1.06); }
  </style>
</head>
<body>
  <main class="error-card">
    <h1>{{ status }}</h1>
    <p>Algo salió mal. Vuelve al inicio e inténtalo nuevamente.</p>
    <a href="{{ url_for('public.home') }}">Volver al inicio</a>
  </main>
</body>
</html>
"""

# ============================================================
# 3. partials/theme_head.html
# ============================================================
FILES["partials/theme_head.html"] = r"""{# Runs synchronously before styles and the first paint; never consult OS preference. #}
<script>
(function () {
  var theme = 'dark';
  try { if (localStorage.getItem('theme') === 'light') theme = 'light'; } catch (_) {}
  document.documentElement.dataset.theme = theme;
  document.documentElement.style.colorScheme = theme;
})();
</script>
<link rel="stylesheet" href="{{ url_for('static', filename='css/theme-tokens.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/responsive-tokens.css') }}">
<script src="{{ url_for('static', filename='js/theme.js') }}"></script>
"""

# ============================================================
# 4. partials/flash.html
# ============================================================
FILES["partials/flash.html"] = r"""{% with messages = get_flashed_messages(with_categories=true) %}
  {% if messages %}
    <div class="flash-container" role="status" aria-live="polite">
      {% for category, message in messages %}
        <div class="flash flash-{{ category }}">{{ message }}</div>
      {% endfor %}
    </div>
  {% endif %}
{% endwith %}
"""

# ============================================================
# 5. partials/header.html
# ============================================================
FILES["partials/header.html"] = r"""{%- set sr_icons = {
  'compass': 'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0 M15.5 8.5l-2 5-5 2 2-5z',
  'basket-shopping': 'M3 10h18l-2 10H5z M7 10l4-7m6 7-4-7',
  'heart': 'M12 20S3 15 3 8a5 5 0 0 1 9-2 5 5 0 0 1 9 2c0 7-9 12-9 12z',
  'receipt': 'M5 3h14v18l-3-2-4 2-4-2-3 2z M8 8h8m-8 4h6',
  'comment': 'M21 11a9 8 0 0 1-9 8H9l-5 2 1-5a9 8 0 1 1 16-5z',
  'bell': 'M4 17h16l-2-3v-4a6 6 0 0 0-12 0v4z M10 20q2 2 4 0',
  'life-ring': 'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0 M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0 M5.5 5.5l3.5 3.5m6 6 3.5 3.5m-13 0L9 15m6-6 3.5-3.5',
  'store': 'M3 10l2-6h14l2 6q-2 3-5 0-4 3-8 0-3 3-5 0 M5 12v8h14v-8 M10 20v-6h4v6',
  'user': 'M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0 M4 21v-2a8 6 0 0 1 16 0v2',
  'lock': 'M5 10h14v11H5z M8 10V7a4 4 0 0 1 8 0v3',
  'bars': 'M3 6h18M3 12h18M3 18h18',
  'arrow-right-from-bracket': 'M10 3H4v18h6 M9 12h12m-5-5 5 5-5 5',
  'chart-line': 'M3 3v18h18 M6 15l4-6 4 3 6-8',
  'chart-pie': 'M10 3a9 9 0 1 0 11 11H10z M13 2v9h9a10 10 0 0 0-9-9z',
  'users': 'M14 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0 M2 20a8 6 0 0 1 16 0 M17 4a4 4 0 0 1 0 7m1 3q4 1 4 6',
  'tags': 'M3 3h8l10 10-8 8L3 11z M7 7h1',
  'shield-halved': 'M12 2l8 4v6q0 6-8 10-8-4-8-10V6z M12 5v13',
  'sliders': 'M3 6h8m4 0h6M3 17h4m4 0h10 M11 3v6m-4 5v6',
  'circle-plus': 'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0 M7 12h10m-5-5v10',
  'user-plus': 'M12 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0 M2 20a6 6 0 0 1 12 0m2-9h7m-3.5-3.5v7'
} -%}

{%- macro glyph(name) -%}
<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="{{ sr_icons.get(name, '')|e }}"/></svg>
{%- endmacro -%}

{%- macro navlink(endpoint, label, icon) -%}
{%- if endpoint.startswith('#') -%}
<a href="#" data-pendiente="{{ endpoint[1:] }}" title="Próximamente" aria-disabled="true">{{ glyph(icon) }}<span>{{ label }}</span></a>
{%- else -%}
<a href="{{ url_for(endpoint) }}" title="{{ label }}" {% if request.endpoint == endpoint %}aria-current="page"{% endif %}>{{ glyph(icon) }}<span>{{ label }}</span></a>
{%- endif -%}
{%- endmacro -%}

{%- macro navsection(label, icon, links) -%}
  {%- set ns = namespace(active=false) -%}
  {%- for link in links -%}
    {%- if request.endpoint == link[0] -%}{% set ns.active = true %}{% endif -%}
  {%- endfor -%}
  <details class="sr-nav-section" name="admin-navigation"{% if ns.active %} open{% endif %}>
    <summary title="{{ label }}"{% if ns.active %} class="sr-section-active"{% endif %}>
      {{ glyph(icon) }}<span class="sr-section-label">{{ label }}</span><svg class="sr-section-chevron" aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="m8 10 4 4 4-4"/></svg>
    </summary>
    <div class="sr-section-links">
      {%- for endpoint, text, symbol in links -%}
        {%- if endpoint.startswith('#') -%}
        <a href="#" data-pendiente="{{ endpoint[1:] }}" title="Próximamente" aria-disabled="true">{{ glyph(symbol) }}<span>{{ text }}</span></a>
        {%- else -%}
        <a href="{{ url_for(endpoint) }}" title="{{ text }}" {% if request.endpoint == endpoint %}aria-current="page"{% endif %}>{{ glyph(symbol) }}<span>{{ text }}</span></a>
        {%- endif -%}
      {%- endfor -%}
    </div>
  </details>
{%- endmacro -%}

{%- set user = session.get('user') -%}
{%- if user is not mapping or not user.get('id') -%}{% set user = none %}{% endif -%}
<header class="sr-header">
  <div class="sr-top">
    <button class="sr-icon sr-menu-button" type="button" aria-controls="sr-navigation" aria-expanded="false" aria-label="Abrir navegación">{{ glyph('bars') }}</button>
    <a class="sr-logo" href="{{ url_for('public.home') }}" aria-label="SmartResto, inicio">
      <span class="sr-mark" aria-hidden="true">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
          <path d="M5 3v5m3-5v5m3-5v5M5 7q0 5 3 5t3-5M8 12v9M18 3c-4 4-4 9 0 9V3zm0 9v9"/>
        </svg>
      </span>{{ website.brand }}
    </a>

    {% if sr_saas_private %}
    <a class="saas-context" href="#">{% if user %}{{ 'Mi empresa' if user.role == 'business_owner' else 'Administración' if user.role == 'admin' else 'Personal' }}{% else %}Personal{% endif %} <span aria-hidden="true">⌄</span></a>
    <nav class="saas-global-links" aria-label="Navegación global">
      <a href="{{ url_for('public.home') }}">Ver sitio web</a>
      <a href="#" data-pendiente="comunicacion.inbox" aria-disabled="true">Mensajes</a>
    </nav>
    {% else %}
    <nav class="sr-public-links" aria-label="Descubrir">
      <a href="{{ url_for('public.home') }}" {% if request.endpoint == 'public.home' %}aria-current="page"{% endif %}>Descubrir</a>
      <a href="{{ url_for('discovery.index') }}" {% if request.endpoint == 'discovery.index' %}aria-current="page"{% endif %}>Restaurantes</a>
      <a href="{{ url_for('market.index') }}" {% if request.endpoint == 'market.index' %}aria-current="page"{% endif %}>Mercado</a>
      <a href="{{ url_for('ar.index') }}" {% if request.endpoint == 'ar.index' %}aria-current="page"{% endif %}>Menú 3D</a>
      <a href="#" data-pendiente="main.business_plans" aria-disabled="true">Para negocios</a>
    </nav>
    {% endif %}

    <div class="sr-actions">
      <a class="sr-icon sr-favorites-link" href="#" data-pendiente="auth.favorites" aria-label="Mis favoritos" title="Mis favoritos (próximamente)" aria-disabled="true">{{ glyph('heart') }}</a>
      <button id="themeToggle" type="button" class="theme-toggle" data-theme-toggle aria-label="Tema oscuro" aria-pressed="true">
        <span aria-hidden="true" data-theme-icon>☀</span><span data-theme-label>Usar tema claro</span>
      </button>
      {% if user %}
        <a class="sr-icon" href="#" data-pendiente="comunicacion.notifications" aria-label="Notificaciones" aria-disabled="true">{{ glyph('bell') }}</a>
        <a class="sr-icon sr-message-link" href="#" data-pendiente="comunicacion.inbox" aria-label="Mensajes" aria-disabled="true">{{ glyph('comment') }}</a>
        <div class="private-account">
          <button type="button" class="sr-account" data-account-toggle aria-expanded="false" aria-controls="private-account-menu" aria-label="Abrir opciones de cuenta">{{ (user.get('profile', {}).get('name') or user.get('username') or 'U')[0]|upper }}</button>
          <div id="private-account-menu" class="private-account-menu" hidden>
            <a href="#" data-pendiente="auth.profile" aria-disabled="true">Mi perfil</a>
            <a href="#" data-pendiente="auth.account_security" aria-disabled="true">Configuración y seguridad</a>
            {% if sr_saas_private %}
            <a href="{{ url_for('public.home') }}">Ir al sitio web</a>
            {% else %}
            <a href="{{ url_for('admin.dashboard' if user.role == 'admin' else 'owner.dashboard' if user.role == 'business_owner' else 'market.index') }}">Ir al sistema</a>
            {% endif %}
            <a href="{{ url_for('auth.logout') }}">Cerrar sesión</a>
          </div>
        </div>
      {% else %}
        <a class="sr-login" href="{{ url_for('auth.login_form') }}">Ingresar</a>
        <a class="sr-button sr-signup" href="{{ url_for('auth.register_form') }}">Crear cuenta</a>
      {% endif %}
    </div>
  </div>
</header>

<button class="sr-backdrop" hidden aria-label="Cerrar navegación"></button>

{% if not sr_private %}
<nav class="sr-public-menu" id="sr-navigation" aria-label="Navegación del sitio web">
  <div class="sr-public-menu-top"><strong>Explora SmartResto</strong><button type="button" class="sr-icon sr-collapse" aria-label="Cerrar navegación">×</button></div>
  {{ navlink('public.home','Descubrir','compass') }}
  {{ navlink('discovery.index','Restaurantes','store') }}
  {{ navlink('market.index','Mercado gastronómico','basket-shopping') }}
  {{ navlink('ar.index','Menú 3D','chart-line') }}
  {{ navlink('loyalty.index','Recompensas','tags') }}
  {% if user %}
    {{ navlink('admin.dashboard' if user.role == 'admin' else 'owner.dashboard' if user.role == 'business_owner' else 'market.index','Mi espacio','user') }}
  {% else %}
    {{ navlink('auth.login_form','Ingresar','user') }}
    {{ navlink('auth.register_form','Crear cuenta','user-plus') }}
  {% endif %}
</nav>
{% else %}
<nav class="sr-sidebar" id="sr-navigation" aria-label="Menú principal">
  <div class="sr-side-top">
    <strong class="sr-group">Navegación</strong>
    <button type="button" class="sr-icon sr-collapse" aria-controls="sr-navigation" aria-expanded="false" aria-label="Expandir menú" title="Expandir menú">
      <svg class="sr-collapse-arrow" aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="m9 6 6 6-6 6"/></svg>
      <svg class="sr-collapse-close" aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="m6 6 12 12M18 6 6 18"/></svg>
    </button>
  </div>

  {% if user and user.role == 'admin' %}
    {{ navlink('admin.dashboard','Resumen','chart-pie') }}
    {{ navlink('#intelligence.dashboard','Inteligencia empresarial','chart-line') }}
    {{ navlink('#trust_center.dashboard','Seguridad y confianza','shield-halved') }}
    {{ navlink('#copilot.page','SmartResto Copilot','comment') }}
    {{ navsection('Restaurantes','store',[
      ('#companies.admin_companies','Empresas y suscripciones','store'),
      ('#commercial_radar.dashboard','Radar comercial','compass'),
      ('#admin.restaurants','Todos los restaurantes','store'),
      ('#admin.new_restaurant','Registrar restaurante','circle-plus'),
      ('#admin.categories','Categorías','tags')]) }}
    {{ navsection('Moderación','shield-halved',[
      ('#admin.moderation_dashboard','Moderación','shield-halved'),
      ('#discovery.dashboard','Radar gastronómico','compass'),
      ('#admin.users','Usuarios y roles','users'),
      ('#admin.operations','Pedidos y pagos','receipt')]) }}
    {{ navsection('Configuración','sliders',[
      ('#admin.controls','Configuración y auditoría','sliders'),
      ('#admin.website_settings','Configuración del sitio web','sliders')]) }}
  {% elif user and user.role == 'business_owner' %}
    <strong class="sr-group">Mi empresa</strong>
    {{ navlink('owner.dashboard','Resumen de mi empresa','chart-pie') }}
    {{ navlink('salon.index','Salón y mesas','store') }}
    {{ navlink('kitchen.index','Cocina','basket-shopping') }}
    {{ navlink('market.index','Mercado','basket-shopping') }}
    {{ navlink('loyalty.index','Recompensas','tags') }}
    <strong class="sr-group">Mi espacio</strong>
  {% else %}
    <strong class="sr-group">Mi espacio</strong>
    {{ navlink('market.index','Mis pedidos','receipt') }}
    {{ navlink('loyalty.index','Mis puntos','tags') }}
    {{ navlink('#auth.favorites','Favoritos','heart') }}
  {% endif %}

  {% if user %}
    <div class="saas-sidebar-footer">
      <form method="post" action="{{ url_for('auth.logout') }}">
        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
        <button type="submit" title="Cerrar sesión">{{ glyph('arrow-right-from-bracket') }}<span>Cerrar sesión</span></button>
      </form>
    </div>
  {% endif %}
</nav>
{% endif %}
"""

# ============================================================
# 6. partials/footer.html
# ============================================================
FILES["partials/footer.html"] = r"""{% if show_public_footer is not defined or show_public_footer %}
<footer class="sr-footer sr-unified-footer">
  <div class="sr-footer-grid">
    <div class="sr-footer-brand">
      <a class="sr-logo" href="{{ url_for('public.home') }}">{{ website.brand }}</a>
      <p>{{ website.tagline }}</p>
      <a href="tel:{{ website.phone }}">{{ website.phone }}</a>
      {% if website.email %}<a href="mailto:{{ website.email }}">{{ website.email }}</a>{% endif %}
    </div>
    <nav aria-label="Descubrir">
      <strong>Descubrir</strong>
      <a href="{{ url_for('discovery.index') }}">Restaurantes</a>
      <a href="{{ url_for('market.index') }}">Mercado gastronómico</a>
      <a href="{{ url_for('ar.index') }}">Menú 3D</a>
    </nav>
    <nav aria-label="Tu espacio">
      <strong>Tu espacio</strong>
      <a href="{{ url_for('auth.register_form') }}">Crear cuenta</a>
      <a href="{{ url_for('loyalty.index') }}">Recompensas</a>
    </nav>
    <nav aria-label="Ayuda y transparencia">
      <strong>Ayuda y transparencia</strong>
      <a href="#" data-pendiente="main.information" aria-disabled="true">Política de privacidad</a>
      <a href="#" data-pendiente="main.information" aria-disabled="true">Términos y condiciones</a>
      <a href="#" data-pendiente="main.information" aria-disabled="true">Contacto</a>
    </nav>
  </div>
  <div class="sr-footer-bottom">
    <span>© {{ now_year }} {{ website.brand }}</span>
    <span>Hecho para descubrir y compartir la gastronomía local.</span>
  </div>
</footer>
{% endif %}
"""

# ============================================================
# 7. partials/mobile_navigation.html
# ============================================================
FILES["partials/mobile_navigation.html"] = r"""{% if not sr_authenticated or (shell_user is mapping and shell_user.get('role') in ('user', 'diner')) %}
{% from 'partials/header.html' import glyph with context %}
<nav class="sr-mobile-nav" aria-label="Accesos rápidos">
  <a href="{{ url_for('public.home') }}" {% if request.endpoint == 'public.home' %}aria-current="page"{% endif %}>{{ glyph('compass') }}<span>Explorar</span></a>
  <a href="{{ url_for('discovery.index') }}" {% if request.endpoint == 'discovery.index' %}aria-current="page"{% endif %}>{{ glyph('heart') }}<span>Para ti</span></a>
  <a href="{{ url_for('market.index') }}" {% if request.endpoint == 'market.index' %}aria-current="page"{% endif %}>{{ glyph('basket-shopping') }}<span>Mercado</span></a>
  <a href="{{ url_for('market.index') if sr_authenticated else url_for('auth.login_form') }}" {% if request.endpoint in ('market.index', 'auth.login_form') %}aria-current="page"{% endif %}>{{ glyph('user') }}<span>{{ 'Pedidos' if sr_authenticated else 'Ingresar' }}</span></a>
</nav>
{% endif %}
"""

# ============================================================
# 8. partials/location_consent.html
# ============================================================
FILES["partials/location_consent.html"] = r"""<aside class="sr-location-consent" id="location-consent" aria-label="Preferencias de ubicación" hidden>
  <div><strong>Descubre lo que tienes cerca</strong><p>¿Permites usar tu ubicación para encontrar restaurantes cercanos y adaptar las recomendaciones al clima? Tu navegador solicitará permiso. Puedes cambiar esta decisión en cualquier momento.</p></div>
  <button type="button" data-location-accept>Aceptar y activar</button>
  <button type="button" class="secondary" data-location-decline>Ahora no</button>
  <output role="status" data-location-status></output>
</aside>
"""

# ============================================================
# 9. partials/theme_toggle.html (para usar inline en header)
# ============================================================
FILES["partials/theme_toggle.html"] = r"""<button type="button" class="theme-toggle" data-theme-toggle aria-label="Tema oscuro" aria-pressed="true">
  <span aria-hidden="true" data-theme-icon><svg viewBox="0 0 24 24" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l2 2m10 10 2 2M5 19l2-2M17 7l2-2M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0"/></svg></span>
  <span data-theme-label>Usar tema claro</span>
</button>
"""

# ============================================================
# 10. partials/brand_defaults.html
# ============================================================
FILES["partials/brand_defaults.html"] = r"""{% set default_primary = '#245447' %}
{% set default_secondary = '#D8A65D' %}
"""

# ============================================================
# 11. partials/internal_workspace_header.html
# ============================================================
FILES["partials/internal_workspace_header.html"] = r"""{%- set workspace_user = session.get('user', {}) -%}
{%- set owner_space = workspace_user.get('role') == 'business_owner' -%}
{%- set workspace_titles = {
  'admin.dashboard': 'Centro de control', 'owner.dashboard': 'Resumen de mi empresa',
  'salon.index': 'Salón y mesas', 'kitchen.index': 'Cocina en vivo',
  'market.index': 'Mercado gastronómico', 'loyalty.index': 'Recompensas',
  'ar.index': 'Menú 3D'
} -%}
{%- set workspace_title = workspace_titles.get(request.endpoint, 'Espacio de trabajo') -%}
<div class="sr-workspace-header">
  <div>
    <nav class="sr-workspace-crumbs" aria-label="Ruta de navegación">
      <span>SmartResto</span><span aria-hidden="true">/</span>
      <span>{{ 'Mi empresa' if owner_space else 'Administración' if workspace_user.get('role') == 'admin' else 'Personal' }}</span>
      <span aria-hidden="true">/</span><strong>{{ workspace_title }}</strong>
    </nav>
    <p class="sr-workspace-kicker">{{ 'OPERACIÓN COMERCIAL' if owner_space else 'OPERACIÓN DE PLATAFORMA' if workspace_user.get('role') == 'admin' else 'ESPACIO PERSONAL' }}</p>
  </div>
</div>
"""

# ============================================================
# 12. auth/login.html
# ============================================================
FILES["auth/login.html"] = r"""{% extends "base.html" %}
{% block title %}Iniciar sesión · {{ APP_NAME }}{% endblock %}

{% block content %}
<div id="ax-stage" class="ax-stage" data-mode="login" data-login-url="{{ url_for('auth.login_form') }}" data-register-url="{{ url_for('auth.register_form') }}">
  <div class="ax-visual" aria-hidden="true">
    <div class="ax-food-host" data-food-experience-api>
      <div class="ax-food-canvas">
        <img data-scene-fallback src="{{ url_for('static', filename='images/auth/lomo.webp') }}" alt="Lomo saltado con papas y arroz">
      </div>
      <div class="ax-food-caption">
        <h3>Lomo saltado</h3>
        <p>Cocina peruana · sabores con carácter</p>
      </div>
    </div>
  </div>
  <div class="ax-forms">
    {% include 'partials/flash.html' %}
    <div class="ax-panes">
      <section class="ax-pane ax-pane-login" data-pane="login" aria-labelledby="ax-login-title">
        <div class="ax-card">
          <p class="ax-eyebrow"><span class="ax-mark" aria-hidden="true">✦</span> SmartResto</p>
          <h1 id="ax-login-title" class="ax-title">Bienvenido de nuevo</h1>
          <p class="ax-subtitle">Ingresa para descubrir, pedir y disfrutar.</p>
          <form class="ax-form" method="post" action="{{ url_for('auth.login_submit') }}" novalidate>
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
            <input type="hidden" name="next" value="{{ next or '' }}">
            <div class="ax-field">
              <label class="ax-label" for="ax-login-username">Usuario o correo</label>
              <div class="ax-control">
                <svg class="ax-lead" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0M4 21v-2a8 6 0 0 1 16 0v2"/></svg>
                <input id="ax-login-username" name="username" type="text" autocomplete="username" required value="{{ username or '' }}" placeholder="tu usuario o correo">
              </div>
              <p class="ax-error" data-error-for="ax-login-username" hidden></p>
            </div>
            <div class="ax-field">
              <label class="ax-label" for="ax-login-password">Contraseña</label>
              <div class="ax-control">
                <svg class="ax-lead" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M5 10h14v11H5zM8 10V7a4 4 0 0 1 8 0v3"/></svg>
                <input id="ax-login-password" name="password" type="password" autocomplete="current-password" required placeholder="••••••••">
                <button type="button" class="ax-eye" data-toggle-password="ax-login-password" aria-label="Mostrar contraseña" aria-pressed="false">
                  <svg data-eye-open aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/><circle cx="12" cy="12" r="3"/></svg>
                  <svg data-eye-closed hidden aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24M1 1l22 22"/></svg>
                </button>
              </div>
              <p class="ax-error" data-error-for="ax-login-password" hidden></p>
            </div>
            <button type="submit" class="ax-submit">
              <span class="ax-spinner" aria-hidden="true"></span>
              Ingresar
            </button>
          </form>
          <p class="ax-switch">¿No tienes cuenta? <a href="{{ url_for('auth.register_form') }}">Crear cuenta</a></p>
          <div class="ax-links">
            <a class="ax-link" href="#" data-pendiente="auth.recover" aria-disabled="true">¿Olvidaste tu contraseña?</a>
          </div>
        </div>
      </section>
    </div>
  </div>
</div>
{% endblock %}

{% block scripts %}
<script defer src="{{ url_for('static', filename='js/auth.js') }}"></script>
<script defer src="{{ url_for('static', filename='js/auth/food-scene-loader.js') }}"
        data-scene-module="{{ url_for('static', filename='js/auth/food-scene.js') }}"></script>
{% endblock %}
"""

# ============================================================
# 13. auth/register.html
# ============================================================
FILES["auth/register.html"] = r"""{% extends "base.html" %}
{% block title %}Crear cuenta · {{ APP_NAME }}{% endblock %}

{% block content %}
<div id="ax-stage" class="ax-stage" data-mode="register" data-login-url="{{ url_for('auth.login_form') }}" data-register-url="{{ url_for('auth.register_form') }}">
  <div class="ax-visual" aria-hidden="true">
    <div class="ax-food-host" data-food-experience-api>
      <div class="ax-food-canvas">
        <img data-scene-fallback src="{{ url_for('static', filename='images/auth/ceviche.webp') }}" alt="Ceviche norteño con camote y choclo">
      </div>
      <div class="ax-food-caption">
        <h3>Ceviche norteño</h3>
        <p>Frescura del norte · inspiración marina</p>
      </div>
    </div>
  </div>
  <div class="ax-forms">
    {% include 'partials/flash.html' %}
    <div class="ax-panes">
      <section class="ax-pane ax-pane-register" data-pane="register" aria-labelledby="ax-register-title">
        <div class="ax-card">
          <p class="ax-eyebrow"><span class="ax-mark" aria-hidden="true">✦</span> SmartResto</p>
          <h1 id="ax-register-title" class="ax-title">Crea tu cuenta</h1>
          <p class="ax-subtitle">Descubre restaurantes, guarda favoritos y pide en minutos.</p>
          <form class="ax-form" method="post" action="{{ url_for('auth.register_submit') }}" novalidate>
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
            <div class="ax-field">
              <label class="ax-label" for="ax-reg-name">Nombre completo</label>
              <div class="ax-control">
                <svg class="ax-lead" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0M4 21v-2a8 6 0 0 1 16 0v2"/></svg>
                <input id="ax-reg-name" name="name" type="text" autocomplete="name" required value="{{ name or '' }}" placeholder="Tu nombre completo">
              </div>
              <p class="ax-error" data-error-for="ax-reg-name" hidden></p>
            </div>
            <div class="ax-field">
              <label class="ax-label" for="ax-reg-username">Usuario</label>
              <div class="ax-control">
                <svg class="ax-lead" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0M4 21v-2a8 6 0 0 1 16 0v2"/></svg>
                <input id="ax-reg-username" name="username" type="text" autocomplete="username" required minlength="3" maxlength="80" value="{{ username or '' }}" placeholder="mínimo 3 caracteres">
              </div>
              <p class="ax-error" data-error-for="ax-reg-username" hidden></p>
            </div>
            <div class="ax-field">
              <label class="ax-label" for="ax-reg-email">Correo</label>
              <div class="ax-control">
                <svg class="ax-lead" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M4 4h16v16H4zM4 8l8 6 8-6"/></svg>
                <input id="ax-reg-email" name="email" type="email" autocomplete="email" required value="{{ email or '' }}" placeholder="tucorreo@ejemplo.com">
              </div>
              <p class="ax-error" data-error-for="ax-reg-email" hidden></p>
            </div>
            <div class="ax-field">
              <label class="ax-label" for="ax-reg-password">Contraseña</label>
              <div class="ax-control">
                <svg class="ax-lead" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M5 10h14v11H5zM8 10V7a4 4 0 0 1 8 0v3"/></svg>
                <input id="ax-reg-password" name="password" type="password" autocomplete="new-password" required minlength="8" placeholder="mínimo 8 caracteres">
                <button type="button" class="ax-eye" data-toggle-password="ax-reg-password" aria-label="Mostrar contraseña" aria-pressed="false">
                  <svg data-eye-open aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/><circle cx="12" cy="12" r="3"/></svg>
                  <svg data-eye-closed hidden aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24M1 1l22 22"/></svg>
                </button>
              </div>
              <div class="ax-strength" id="ax-strength" data-score="0" aria-hidden="true"><span></span><span></span><span></span><span></span></div>
              <p class="ax-hint" id="ax-strength-text">Usa al menos 8 caracteres con letras y números.</p>
              <p class="ax-error" data-error-for="ax-reg-password" hidden></p>
            </div>
            <div class="ax-field">
              <label class="ax-label" for="ax-reg-confirm">Confirmar contraseña</label>
              <div class="ax-control">
                <svg class="ax-lead" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M5 10h14v11H5zM8 10V7a4 4 0 0 1 8 0v3"/></svg>
                <input id="ax-reg-confirm" name="confirm" type="password" autocomplete="new-password" required placeholder="repítela">
              </div>
              <p class="ax-error" data-error-for="ax-reg-confirm" hidden></p>
            </div>
            <button type="submit" class="ax-submit">
              <span class="ax-spinner" aria-hidden="true"></span>
              Crear cuenta
            </button>
          </form>
          <p class="ax-switch">¿Ya tienes cuenta? <a href="{{ url_for('auth.login_form') }}">Ingresar</a></p>
        </div>
      </section>
    </div>
  </div>
</div>
{% endblock %}

{% block scripts %}
<script defer src="{{ url_for('static', filename='js/auth.js') }}"></script>
<script defer src="{{ url_for('static', filename='js/auth/food-scene-loader.js') }}"
        data-scene-module="{{ url_for('static', filename='js/auth/food-scene.js') }}"></script>
{% endblock %}
"""

# ============================================================
# 14. public/home.html
# ============================================================
FILES["public/home.html"] = r"""{% extends "base.html" %}
{% from 'partials/header.html' import glyph with context %}

{% block title %}Descubre restaurantes · {{ APP_NAME }}{% endblock %}

{% block head %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/forest-home.css') }}" />
{% endblock %}

{% block content %}
<div class="forest-shell">

  <form id="search-form" class="forest-search" role="search" action="{{ url_for('discovery.index') }}" method="get">
    <div class="forest-search-row">
      <label class="forest-city">
        <span class="sr-only">Elegir distrito</span>
        <select id="forest-district" aria-label="Elegir lugar">
          <option value="">{{ CIUDAD }}, Perú</option>
        </select>
      </label>
      <label class="forest-query">
        <i class="fas fa-magnifying-glass" aria-hidden="true"></i>
        <span class="sr-only">Buscar restaurantes o platos</span>
        <input type="search" id="forest-query" name="q" maxlength="300" placeholder="¿Qué se te antoja hoy? Busca restaurantes o platos…" autocomplete="off">
      </label>
      <button class="forest-search-submit" type="submit" aria-label="Buscar restaurantes">
        <i class="fas fa-magnifying-glass" aria-hidden="true"></i>
      </button>
      <button id="recommendationBtn" class="forest-ai-search" type="button">
        <i class="fas fa-wand-magic-sparkles" aria-hidden="true"></i> Buscar con IA
      </button>
    </div>
  </form>

  <section class="forest-hero" aria-labelledby="forest-headline">
    <div class="forest-hero-copy">
      <p class="forest-campaign"><span></span> Selección de hoy</p>
      <h1 id="forest-headline">Sabores del norte,<br>a un paso de ti</h1>
      <p>Descubre los mejores restaurantes de {{ CIUDAD }}<br class="forest-desktop-break"> y vive una experiencia gastronómica única.</p>
      <div class="forest-hero-actions">
        <a class="forest-light-button" href="#explorar">Explorar restaurantes <i class="fas fa-chevron-right" aria-hidden="true"></i></a>
        <a class="forest-hero-personal" href="{{ url_for('discovery.index') }}">Para ti <i class="fas fa-arrow-right" aria-hidden="true"></i></a>
      </div>
    </div>
    <div class="forest-hero-photo sr-editorial-slides"
         data-editorial-slides='{{ [editorial_images.home, "/static/images/auth/lomo.webp", "/static/images/auth/ceviche.webp"]|tojson }}'>
      <img src="{{ editorial_images.home }}" alt="Inspiración gastronómica peruana" width="1100" height="734" fetchpriority="high">
      <span>Imagen editorial ilustrativa · IA</span>
      <button type="button" data-slide-next aria-label="Ver otro plato">Otro plato</button>
      <button type="button" data-slide-pause aria-label="Pausar cambio de platos">Pausar</button>
    </div>
  </section>

  <nav class="forest-categories" aria-label="Categorías gastronómicas">
    <button type="button" class="filter-chip active" data-filter="all" aria-pressed="true"><i class="fas fa-utensils" aria-hidden="true"></i>Restaurantes</button>
    {% for cat in categories[:5] %}
    <button type="button" class="filter-chip category-chip" data-category="{{ cat.id_categoria }}" aria-pressed="false">
      <i class="fas fa-bowl-food" aria-hidden="true"></i>{{ cat.nombre }}
    </button>
    {% endfor %}
    <a href="{{ url_for('market.index') }}"><i class="fas fa-motorcycle" aria-hidden="true"></i>Delivery</a>
  </nav>

  <section id="explorar" class="forest-restaurants" aria-labelledby="forest-restaurants-title">
    <div class="forest-section-heading">
      <div>
        <h2 id="forest-restaurants-title">Restaurantes destacados en {{ CIUDAD }}</h2>
        <p>Lugares que vale la pena descubrir</p>
      </div>
      <div class="forest-result-actions">
        <a class="forest-outline" href="{{ url_for('discovery.index') }}">Ver todos los restaurantes <span aria-hidden="true">→</span></a>
      </div>
    </div>
    <div class="forest-results-toolbar">
      <p id="resultsCount" role="status" aria-live="polite">{{ restaurants|length if restaurants else 0 }} restaurantes encontrados</p>
    </div>
    <div id="resultsGrid" class="results-grid">
      {% for r in restaurants %}
        {% include 'public/partials/forest_card.html' %}
      {% else %}
      <div class="empty-state">
        <h3>Tu próximo descubrimiento está en camino</h3>
        <p>Todavía no hay restaurantes publicados. Vuelve pronto.</p>
      </div>
      {% endfor %}
    </div>
  </section>

  <section id="ofertas" class="forest-offers" aria-labelledby="forest-offers-title">
    <div class="forest-section-heading">
      <div>
        <h2 id="forest-offers-title">Antojos para disfrutar hoy</h2>
        <p>Explora sabores; consulta precios y disponibilidad en cada negocio.</p>
      </div>
      <a class="forest-text-link" href="{{ url_for('market.index') }}">Explorar el mercado <span aria-hidden="true">→</span></a>
    </div>
    <div class="forest-promo-grid">
      {% for title, subtitle, image in [
        ('Sabores del mar', 'Frescura con acento norteño', 'marine-inspiration.webp'),
        ('Cocina criolla', 'Los sabores de siempre', 'creole-inspiration.webp'),
        ('El almuerzo de hoy', 'Encuentra tu próximo favorito', 'food-inspiration.webp')
      ] %}
      <a class="forest-promo" href="{{ url_for('market.index') }}">
        <img src="{{ url_for('static', filename='images/forest/' ~ image) }}" alt="" loading="lazy">
        <div>
          <h3>{{ title }}</h3>
          <p>{{ subtitle }}</p>
          <span>Explorar platos</span>
        </div>
      </a>
      {% endfor %}
    </div>
  </section>

  <section class="forest-recommendation" aria-labelledby="forest-recommendation-title">
    <img class="forest-chef" src="{{ url_for('static', filename='images/forest/chef-reference.webp') }}" alt="" width="170" height="105" loading="lazy">
    <div class="forest-recommendation-copy">
      <h2 id="forest-recommendation-title">¿No sabes qué elegir?</h2>
      <p>Cuéntanos qué se te antoja y encontramos algo para ti.</p>
    </div>
    <form id="forest-craving-form" onsubmit="event.preventDefault(); document.getElementById('recommendationBtn')?.click();">
      <label class="sr-only" for="forest-craving">Describe lo que te gustaría comer</label>
      <input id="forest-craving" type="text" maxlength="300" placeholder="Ej: algo ligero, criollo o con pollo…" required>
      <button type="submit" id="forest-recommend">
        <i class="fas fa-wand-magic-sparkles" aria-hidden="true"></i> Recomendar
      </button>
    </form>
  </section>

  <section id="cerca" class="forest-nearby" aria-labelledby="forest-nearby-title">
    <div>
      <span class="forest-compact-icon"><i class="fas fa-location-dot" aria-hidden="true"></i></span>
      <div>
        <h2 id="forest-nearby-title">Una buena mesa, cerca de ti</h2>
        <p>Explora {{ CIUDAD }} en el mapa o usa tu ubicación para encontrar opciones cercanas.</p>
      </div>
    </div>
    <a class="forest-outline" href="{{ url_for('discovery.index') }}">Ver mapa <span aria-hidden="true">→</span></a>
  </section>

  <section class="forest-business" id="negocios" aria-labelledby="forest-business-title">
    <img src="{{ url_for('static', filename='images/forest/shop-reference.webp') }}" alt="" loading="lazy" width="270" height="90">
    <div>
      <h2 id="forest-business-title">¿Tienes un negocio gastronómico?</h2>
      <p>Hazlo crecer con SmartResto</p>
    </div>
    <a class="forest-light-button" href="{{ url_for('auth.register_form') }}">Crear cuenta de negocio <span aria-hidden="true">→</span></a>
  </section>

</div>
{% endblock %}

{% block scripts %}
<script>
  window.RESTAURANTS_DATA = {{ restaurants|tojson if restaurants else '[]' }};
  window.INITIAL_COORDS = {{ (CENTER_COORDS or [-8.1118, -79.0287])|tojson }};
  window.MONEDA = {{ MONEDA|tojson }};
</script>
<script defer src="{{ url_for('static', filename='js/forest/processor.js') }}"></script>
<script defer src="{{ url_for('static', filename='js/forest/logic-rules.js') }}"></script>
<script defer src="{{ url_for('static', filename='js/forest/ui.js') }}"></script>
<script defer src="{{ url_for('static', filename='js/forest/controller.js') }}"></script>
<script defer src="{{ url_for('static', filename='js/app.js') }}"></script>
<script defer src="{{ url_for('static', filename='js/search.js') }}"></script>
<script defer src="{{ url_for('static', filename='js/map.js') }}"></script>
<script defer src="{{ url_for('static', filename='js/editorial-slides.js') }}"></script>
<script defer src="{{ url_for('static', filename='js/ai-assistant.js') }}"></script>
{% endblock %}
"""

# ============================================================
# 15. public/partials/forest_card.html
# ============================================================
FILES["public/partials/forest_card.html"] = r"""<article class="restaurant-card rc forest-card" data-id="{{ r.id_restaurante }}" data-lat="{{ r.latitud or '' }}" data-lng="{{ r.longitud or '' }}">
  <div class="card-image">
    {% if r.url_imagen %}
    <img src="{{ r.url_imagen }}" alt="{{ r.nombre }}" loading="lazy" width="640" height="480">
    {% else %}
    <div class="forest-photo-missing"><i class="fas fa-utensils" aria-hidden="true"></i><span>Conoce {{ r.nombre }}</span></div>
    {% endif %}
    {% if r.promocion_texto %}
    <span class="forest-promo-badge"><i class="fas fa-tag" aria-hidden="true"></i> Promoción</span>
    {% endif %}
    <button type="button" class="fav-btn" onclick="toggleFavorite({{ r.id_restaurante }}, event)" aria-label="Guardar {{ r.nombre }} en favoritos" aria-pressed="false">
      <i class="far fa-heart" aria-hidden="true"></i>
    </button>
  </div>
  <div class="card-content">
    <h3>{{ r.nombre }}</h3>
    <div class="card-location">
      <i class="fas fa-location-dot" aria-hidden="true"></i>
      <span>{{ r.distrito or 'Ubicación por confirmar' }}</span>
    </div>
    <div class="forest-card-meta">
      <span class="rating">
        <i class="fas fa-star" aria-hidden="true"></i> {{ '%.1f'|format(r.calificacion) if r.calificacion else 'Sin reseñas' }}
        {% if r.cantidad_resenas_reportada %}<small> ({{ r.cantidad_resenas_reportada }} reseñas)</small>{% endif %}
      </span>
      {% if r.hora_apertura and r.hora_cierre %}
      <span class="forest-hours">{{ r.hora_apertura }} – {{ r.hora_cierre }}</span>
      {% endif %}
    </div>
    <p class="card-price">
      {% if r.precio_promedio %}
      <strong>{{ MONEDA }} {{ '%.0f'|format(r.precio_promedio) }}</strong> por persona
      {% else %}
      Consultar precio
      {% endif %}
    </p>
    <div class="forest-card-bottom">
      <a href="{{ url_for('business.show', restaurante_id=r.id_restaurante) }}" class="card-link">Ver restaurante <span aria-hidden="true">→</span></a>
    </div>
  </div>
</article>
"""

# ============================================================
# Copiar
# ============================================================
def main():
    print(f"📁 Instalando templates en: {TPL_DIR}\n")
    for name, content in FILES.items():
        path = TPL_DIR / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        size = len(content)
        print(f"✅ {name:<42} ({size:,} bytes)")
    print(f"\n🎉 {len(FILES)} templates instalados en {TPL_DIR}")

if __name__ == "__main__":
    main()