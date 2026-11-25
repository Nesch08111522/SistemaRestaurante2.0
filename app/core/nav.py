# app/core/nav.py
"""Helpers de navegación. Filtra endpoints pendientes."""
from __future__ import annotations

from typing import Callable


# Endpoints que SÍ existen en el proyecto
_EXISTING_ENDPOINTS = frozenset({
    "public.home",
    "public.api_me",
    "auth.login_form",
    "auth.login_submit",
    "auth.register_form",
    "auth.register_submit",
    "auth.logout",
    "auth.api_whoami",
    "discovery.index",
    "business.show",
    "market.index",
    "owner.dashboard",
    "admin.dashboard",
    "salon.index",
    "kitchen.index",
    "loyalty.index",
    "ar.index",
})


def endpoint_exists(endpoint: str) -> bool:
    """True si el endpoint está en la lista de existentes."""
    return endpoint in _EXISTING_ENDPOINTS


def safe_url(endpoint: str) -> str | None:
    """
    Devuelve la URL del endpoint si existe, o None si está pendiente.
    Uso en templates: {% set url = safe_url('market.cart') %} {% if url %}...{% endif %}
    """
    if not endpoint_exists(endpoint):
        return None
    try:
        from flask import url_for
        return url_for(endpoint)
    except Exception:
        return None


def company_nav_allowed(endpoint: str) -> bool:
    """
    Placeholder. Devuelve True siempre por ahora.
    En el futuro puede chequear permisos de suscripción.
    """
    return True


def register_nav(app):
    app.jinja_env.globals["company_nav_allowed"] = company_nav_allowed
    app.jinja_env.globals["safe_url"] = safe_url
    app.jinja_env.globals["endpoint_exists"] = endpoint_exists