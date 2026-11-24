# app/blueprints/market/__init__.py
"""Blueprint de mercado (delivery / e-commerce)."""
from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from app.core.auth_guard import login_required
from app.models.order import OrderModel
from app.models.restaurant import RestaurantModel

bp = Blueprint("market", __name__, template_folder="../../templates/market")


@bp.get("/")
def index():
    restaurantes = RestaurantModel.list_published(limit=50)
    return render_template("market/index.html", restaurantes=restaurantes)


@bp.get("/api/restaurantes")
def api_restaurantes():
    return jsonify(RestaurantModel.list_published(limit=50)), 200


@bp.get("/api/mis-pedidos")
@login_required
def api_mis_pedidos():
    from flask import session
    user_id = session.get("user_id")
    pedidos = OrderModel.list_by_usuario(int(user_id), limit=50, full=True)
    return jsonify({"total": len(pedidos), "pedidos": pedidos}), 200