# app/blueprints/kitchen/__init__.py
"""Blueprint del KDS (Kitchen Display System)."""
from __future__ import annotations

from flask import Blueprint, jsonify, render_template

from app.core.auth_guard import empresa_required, login_required, role_required
from app.models.order import OrderModel
from app.blueprints.workspace import workspace_errors

bp = Blueprint("kitchen", __name__, template_folder="../../templates/kitchen")


@bp.get("/")
@workspace_errors
@login_required
@empresa_required
@role_required("business_owner", "business_admin", "manager", "kitchen")
def index():
    from .operation_routes import board
    return board()


@bp.get("/api/pedidos")
@login_required
@empresa_required
@role_required("business_owner", "business_admin", "manager", "kitchen")
def api_pedidos():
    from flask import g
    from app.repositories.restaurantes import RestaurantesRepository
    empresa = g.empresa
    restaurantes = RestaurantesRepository.list_by_empresa(empresa["id_empresa"])
    pedidos_pendientes: list[dict] = []
    for r in restaurantes:
        for p in OrderModel.list_by_restaurante(
            r["id_restaurante"], estado="pending", limit=50
        ):
            pedidos_pendientes.append(p)
    return jsonify({"total": len(pedidos_pendientes), "pedidos": pedidos_pendientes}), 200


from . import operation_routes  # noqa: E402,F401
