# app/blueprints/salon/__init__.py
"""Blueprint del salón (mesas en vivo)."""
from __future__ import annotations

from flask import Blueprint, jsonify, render_template

from app.core.auth_guard import empresa_required, login_required, role_required

bp = Blueprint("salon", __name__, template_folder="../../templates/salon")


@bp.get("/")
@login_required
@empresa_required
@role_required("business_owner", "business_admin", "manager", "cashier", "waiter")
def index():
    return render_template("salon/index.html")


@bp.get("/api/mesas")
@login_required
@empresa_required
@role_required("business_owner", "business_admin", "manager", "cashier", "waiter")
def api_mesas():
    """
    El .sql no tiene tabla `mesas` todavía. Se deja endpoint listo
    para conectar en una fase futura con una tabla dedicada.
    """
    return jsonify({"mesas": [], "nota": "Tabla `mesas` pendiente de migración."}), 200