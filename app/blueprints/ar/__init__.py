# app/blueprints/ar/__init__.py
"""Blueprint de menús 3D y realidad aumentada."""
from __future__ import annotations

from flask import Blueprint, jsonify, render_template

bp = Blueprint("ar", __name__, template_folder="../../templates/ar")


@bp.get("/")
def index():
    return render_template("ar/index.html")


@bp.get("/api/modelos/<int:id_plato>")
def api_modelo(id_plato: int):
    """
    Devuelve la referencia al modelo 3D del plato.
    Los modelos se sirven desde `static/assets/models3d/`.
    """
    from app.repositories.platos import PlatosRepository
    plato = PlatosRepository.get_by_id(id_plato)
    if not plato:
        return jsonify({"error": "not_found"}), 404
    return jsonify({
        "id_plato": plato["id_plato"],
        "nombre": plato["nombre"],
        "modelo_url": f"/static/assets/models3d/plato-{id_plato}.glb",
        "nota": "Modelo de referencia; requiere calibración por el negocio.",
    }), 200