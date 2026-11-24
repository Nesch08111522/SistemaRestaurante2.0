# app/core/auth_guard.py
"""
Decoradores de autorización reutilizables.

Se basan en `fresh_session_user()` que ya revalida el usuario contra la BD
en cada request. Estos decoradores añaden:
  - @login_required: exige sesión válida
  - @role_required: exige uno de los roles indicados
  - @permission_required: exige un permiso concreto (ver core.permissions)
  - @empresa_required: exige pertenencia activa a una empresa
"""
from __future__ import annotations

from functools import wraps

from flask import abort, jsonify, redirect, request, url_for

from app.core.permissions import can
from app.core.security import fresh_session_user, is_safe_redirect_url


def _wants_json() -> bool:
    return (
        request.is_json
        or "/api/" in request.path
        or request.accept_mimetypes.best == "application/json"
    )


def _unauthorized():
    if _wants_json():
        return jsonify({"success": False, "error": "No autenticado", "code": "unauthorized"}), 401
    return redirect(url_for("auth.login_form", next=request.path))

def _forbidden(message: str = "No autorizado"):
    if _wants_json():
        return jsonify({"success": False, "error": message, "code": "forbidden"}), 403
    abort(403, description=message)


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = fresh_session_user()
        if not user:
            return _unauthorized()
        return fn(*args, **kwargs)
    return wrapper


def role_required(*roles: str):
    """
    Uso: @role_required("admin") o @role_required("business_owner", "business_admin")
    """
    allowed = set(roles)

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = fresh_session_user()
            if not user:
                return _unauthorized()
            if user.get("role") not in allowed and "admin" not in allowed and user.get("role") != "admin":
                return _forbidden(f"Se requiere rol: {', '.join(sorted(allowed))}")
            if user.get("role") == "admin" and "admin" not in allowed:
                # Admin siempre pasa
                return fn(*args, **kwargs)
            if user.get("role") not in allowed:
                return _forbidden(f"Se requiere rol: {', '.join(sorted(allowed))}")
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def permission_required(permission: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = fresh_session_user()
            if not user:
                return _unauthorized()
            if user.get("role") == "admin":
                return fn(*args, **kwargs)
            if not can(user.get("role"), permission):
                return _forbidden(f"Permiso requerido: {permission}")
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def empresa_required(fn):
    """
    Exige que el usuario en sesión tenga al menos una empresa activa.
    Inyecta `g.empresa` con la empresa principal (o múltiples).
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = fresh_session_user()
        if not user:
            return _unauthorized()
        from app.models.company import get_company_for_user
        empresa = get_company_for_user(user["id"])
        if not empresa:
            return _forbidden("No tienes una empresa activa.")
        from flask import g
        g.empresa = empresa
        return fn(*args, **kwargs)
    return wrapper