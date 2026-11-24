# app/blueprints/pantry/__init__.py
"""Blueprint de Mi cocina inteligente (despensa + recetas)."""
from __future__ import annotations

from flask import Blueprint, jsonify, render_template

from app.core.auth_guard import login_required

bp = Blueprint("pantry", __name__, template_folder="../../templates/pantry")


@bp.get("/")
@login_required
def index():
    return render_template("pantry/index.html")


@bp.get("/api/despensa")
@login_required
def api_despensa():
    """
    Despensa personal. Se usará `cocinas_mercado_despensa` cuando exista
    un identificador de cocina personal del usuario.
    """
    return jsonify({"items": [], "nota": "Despensa personal pendiente de migración."}), 200