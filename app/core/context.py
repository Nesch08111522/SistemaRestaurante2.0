# app/core/context.py
"""Contexto de request por rol + variables globales para templates."""
from __future__ import annotations

import logging
from datetime import date

from flask import g


logger = logging.getLogger(__name__)


# ============================================================
# 1. CONTEXTO GLOBAL (todos los templates)
# ============================================================

def _load_website_config() -> dict:
    """Datos del sitio. Ajusta aquí si luego tienes settings en BD."""
    return {
        "brand": "SmartResto",
        "tagline": "Descubre, pide, disfruta.",
        "phone": "+51999888777",
        "email": "hola@smartresto.pe",
        "instagram": "",
        "facebook": "",
        "tiktok": "",
        "youtube": "",
    }


def _load_editorial_images() -> dict:
    return {
        "home": "/static/images/editorial/home.webp",
        "offers": "/static/images/editorial/offers.webp",
        "business": "/static/images/editorial/business.webp",
    }


def get_global_context(app) -> dict:
    """
    Variables globales para TODOS los templates.
    Se cachea por request en `g` para no repetir consultas.
    """
    if hasattr(g, "_global_context"):
        return g._global_context

    from app.models.company import get_company_for_user

    user = _get_session_user()
    company = None
    if user and user.get("role") == "business_owner":
        try:
            company = getattr(g, "empresa", None) or get_company_for_user(user["id"])
        except Exception as error:
            logger.warning("No se pudo cargar empresa: %s", error)

    website = _load_website_config()
    if company:
        website = {**website, "brand": company.get("nombre") or website["brand"]}

    ctx = {
        "APP_NAME": app.config.get("NOMBRE_APP", "SmartResto"),
        "website": website,
        "now_year": date.today().year,
        "CIUDAD": app.config.get("CIUDAD", "Trujillo"),
        "MONEDA": app.config.get("MONEDA", "S/."),
        "PRIMARY_COLOR": app.config.get("PALETA_PRIMARIA", "#245447"),
        "SECONDARY_COLOR": app.config.get("PALETA_SECUNDARIA", "#D8A65D"),
        "CENTER_COORDS": list(app.config.get("COORDENADAS_CENTRO", (-8.1118, -79.0287))),
        "RADIO_MAXIMO_KM": app.config.get("RADIO_MAXIMO_KM", 10),
        "categories": [],
        "editorial_images": _load_editorial_images(),
        "show_public_footer": True,
        "company": company,
    }
    g._global_context = ctx
    return ctx


# ============================================================
# 2. CONTEXTO POR ROL (nav_role, current_user)
# ============================================================

def _get_session_user() -> dict | None:
    if getattr(g, "database_unavailable", False):
        return None
    from app.core.security import fresh_session_user
    return fresh_session_user()


def _current_context() -> dict:
    user = _get_session_user()
    if not user:
        return {"nav_role": "guest", "current_user": None}

    role = user.get("role") or "user"
    profile = user.get("profile") or {}
    return {
        "nav_role": role,
        "current_user": {
            "id": user.get("id"),
            "username": user.get("username"),
            "role": role,
            "name": profile.get("name"),
            "email": profile.get("email"),
        },
    }


def register_context(app):
    @app.context_processor
    def inject_role_context():
        if hasattr(g, "_role_context"):
            return g._role_context
        ctx = _current_context()
        g._role_context = ctx
        return ctx