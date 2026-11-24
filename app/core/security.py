# app/core/security.py
"""Controles de sesión compartidos por los blueprints."""
from __future__ import annotations

from urllib.parse import urljoin, urlparse

from flask import flash, g, request, session

from app.models.user import UserModel


def is_safe_redirect_url(target: str | None) -> bool:
    """Acepta únicamente destinos locales del mismo host."""
    if not target:
        return False
    ref = urlparse(request.host_url)
    test = urlparse(urljoin(request.host_url, target))
    return test.scheme in {"http", "https"} and test.netloc == ref.netloc


def session_identity(user: dict) -> dict:
    """Construye el mínimo de identidad necesario para la sesión Flask."""
    profile = user.get("profile") or {}
    return {
        "id": user.get("id"),
        "username": user.get("username"),
        "role": user.get("role", "user"),
        "profile": {
            "name": profile.get("name"),
            "email": profile.get("email"),
        },
    }


def current_user_id() -> int | None:
    raw_id = session.get("user_id")
    try:
        return int(raw_id) if raw_id is not None else None
    except (TypeError, ValueError):
        return None


def normalize_text(value: object, *, max_length: int = 500) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().split())[:max_length]


def valid_coordinate(value: object, minimum: float, maximum: float) -> bool:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return False
    return minimum <= numeric <= maximum


def fresh_session_user():
    """
    Revalida el rol contra PostgreSQL antes de autorizar.

    El .sql no tiene auth_epoch. Se valida:
      - que el usuario exista
      - que `estado_cuenta` sea ACTIVE
    """
    if hasattr(g, "session_user_error"):
        raise g.session_user_error
    if hasattr(g, "session_identity"):
        return g.session_identity

    user_id = current_user_id()
    if user_id is None:
        g.session_identity = None
        return None

    from app.db.connection import (
        DatabaseConfigurationError,
        DatabaseConnectionError,
    )
    import psycopg

    try:
        user = UserModel.get_session_account(user_id)
    except (DatabaseConfigurationError, DatabaseConnectionError, psycopg.OperationalError) as error:
        g.session_user_error = error
        raise

    if not UserModel.is_active(user):
        g.session_identity = None
        session.clear()
        flash("Tu sesión expiró. Inicia sesión de nuevo.", "warning")
        return None

    g.account_record = user
    identity = session_identity(user)
    session["user"] = identity
    session["role"] = identity["role"]
    session["username"] = identity["username"]
    g.session_identity = identity
    return identity