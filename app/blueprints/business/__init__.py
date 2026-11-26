# app/blueprints/business/__init__.py
"""Blueprint de página pública del negocio."""
from __future__ import annotations

from flask import Blueprint, abort, jsonify, render_template

from app.models.menu import MenuModel
from app.models.promotion import PromotionModel
from app.models.restaurant import RestaurantModel
from app.models.review import ReviewModel
from app.repositories.platos import PlatosRepository

bp = Blueprint("business", __name__)


@bp.get("/<int:restaurante_id>")
def show(restaurante_id: int):
    restaurante = RestaurantModel.get_by_id(restaurante_id, full=False)
    if not restaurante or restaurante.get('estado_publicacion') != 'published' or restaurante.get('suspendido') or restaurante.get('rechazado'):
        abort(404)
    restaurante = {**restaurante, 'platos': PlatosRepository.list_publicados(restaurante_id)}
    menus = MenuModel.list_by_restaurante(restaurante_id, full=True)
    resenas = ReviewModel.list_by_restaurante(restaurante_id, limit=20)
    resumen = ReviewModel.summary(restaurante_id)
    promociones = PromotionModel.list_by_restaurante(restaurante_id, vigentes=True)
    return render_template(
        "business/show.html",
        restaurante=restaurante,
        menus=menus,
        resenas=resenas,
        resumen=resumen,
        promociones=promociones,
    )


@bp.get("/<int:restaurante_id>/api/menu")
def api_menu(restaurante_id: int):
    restaurante = RestaurantModel.get_by_id(restaurante_id, full=False)
    if not restaurante or restaurante.get('estado_publicacion') != 'published' or restaurante.get('suspendido') or restaurante.get('rechazado'):
        abort(404)
    menu = PlatosRepository.list_publicados(restaurante_id)
    return jsonify({"restaurante_id": restaurante_id, "platos": menu}), 200
