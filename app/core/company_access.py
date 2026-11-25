# app/core/company_access.py
"""
Frontera de suscripción.

Se ejecuta en before_request y valida que el usuario en sesión tenga
permiso sobre la empresa indicada en la ruta o el body.

Nota: en Fase 2, `id_empresa` se busca en:
  - request.view_args["id_empresa"] / ["empresa_id"] / ["bid"]
  - query string o body

Cuando exista RestaurantModel (Fase 3), se podrá resolver también desde
`restaurante_id` -> `id_empresa`.
"""
from __future__ import annotations

from flask import abort, request

from app.models.company import permitted
from app.core.security import fresh_session_user


def enforce_subscription():
    endpoint = request.endpoint or ""
    if endpoint in {"static", "public.home", "health_check"}:
        return

    user = fresh_session_user()
    if not user:
        return
    if user.get("role") == "admin":
        return

    permission = None
    if endpoint.startswith("owner."):
        permission = "catalog.manage"
        if endpoint == "owner.dashboard":
            permission = "business.manage"
        if endpoint in {
            "owner.generate_menu",
            "owner.audit_restaurant_menu",
            "owner.suggest_menu_dish_correction",
        }:
            permission = "ai.business"
    elif endpoint.startswith("catalog.") and request.path.startswith("/owner/"):
        permission = (
            "ai.business"
            if endpoint in {"catalog.photo", "catalog.voice"}
            else "catalog.manage"
        )
    elif endpoint.startswith("sites.") and request.path.startswith("/owner/"):
        permission = "ai.business" if endpoint == "sites.ai" else "site.manage"
    elif endpoint.startswith("intelligence."):
        permission = "analytics.read.business"
    elif endpoint.startswith("copilot.") and user.get("role") in {"owner", "business_owner"}:
        permission = "ai.business"
    elif endpoint.startswith("flow.") and request.path.startswith("/salon/"):
        permission = "flow.manage"
    elif endpoint == "loyalty.customers":
        permission = "loyalty.manage.business"
    elif endpoint.startswith("salon.") and request.path.startswith(("/owner/", "/salon")):
        permission = (
            "tables.manage" if request.path.startswith("/owner/") else "tables.service"
        )
    elif endpoint in {"ecosystem.campaign", "ecosystem.business"}:
        permission = "promotion.manage"
    elif endpoint == "ecosystem.upload_model":
        permission = "ai.business"
    elif endpoint in {"market.copilot", "market.simulate"}:
        permission = "ai.business"
    elif endpoint in {
        "market.publish", "market.configure_coupon", "admin.add_promotion",
    }:
        permission = "promotion.manage"
    elif endpoint.startswith("business_access.") and request.path.startswith("/owner/"):
        permission = (
            "business.manage"
            if endpoint == "business_access.submit_verification"
            else "staff.manage"
        )

    if not permission:
        return

    args = request.view_args or {}
    id_empresa = next(
        (args[k] for k in ("id_empresa", "empresa_id", "bid") if k in args),
        None,
    )
    body = request.get_json(silent=True) if request.is_json else request.form

    if id_empresa is None:
        raw = (
            request.args.get("id_empresa")
            or request.args.get("empresa_id")
            or (body or {}).get("id_empresa")
            or (body or {}).get("empresa_id")
        )
        if raw is not None:
            try:
                id_empresa = int(raw)
            except (ValueError, TypeError):
                abort(400)

    if id_empresa is None:
        abort(400, description="Falta id_empresa en la solicitud.")

    if not permitted(user, int(id_empresa), permission):
        abort(403, description="Tu rol o suscripción no permite esta funcionalidad.")