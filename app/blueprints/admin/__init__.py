# app/blueprints/admin/__init__.py
"""Blueprint del panel de administración de plataforma."""
from __future__ import annotations

from flask import Blueprint, jsonify, render_template

from app.core.auth_guard import login_required, role_required
from app.repositories.empresas import EmpresasRepository
from app.repositories.usuarios import UsuariosRepository

bp = Blueprint("admin", __name__, template_folder="../../templates/admin")


@bp.get("/")
@login_required
@role_required("admin")
def dashboard():
    empresas = EmpresasRepository.list_all(limit=200)
    usuarios = UsuariosRepository.list_by_role("admin", limit=200)
    return render_template(
        "admin/dashboard.html",
        total_empresas=len(empresas),
        empresas=empresas[:10],
        total_admins=len(usuarios),
    )


@bp.get("/api/stats")
@login_required
@role_required("admin")
def api_stats():
    empresas = EmpresasRepository.list_all(limit=1000)
    estados = {}
    for e in empresas:
        estados[e["estado"]] = estados.get(e["estado"], 0) + 1
    return jsonify({
        "total_empresas": len(empresas),
        "empresas_por_estado": estados,
    }), 200