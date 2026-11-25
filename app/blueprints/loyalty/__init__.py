# app/blueprints/loyalty/__init__.py
"""Blueprint de fidelización (puntos, recompensas)."""
from __future__ import annotations

from flask import Blueprint, jsonify, render_template

from app.core.auth_guard import login_required

bp = Blueprint("loyalty", __name__, template_folder="../../templates/loyalty")


@bp.get("/")
@login_required
def index():
    return render_template("loyalty/index.html")


@bp.get("/api/saldo")
@login_required
def api_saldo():
    """
    El .sql no tiene tabla de puntos todavía. Se deja endpoint listo
    para conectar cuando exista `puntos_fidelidad` o similar.
    """
    return jsonify({
        "puntos": 0,
        "nivel": "bronce",
        "nota": "Sistema de puntos pendiente de migración.",
    }), 200