# app/blueprints/admin/__init__.py
"""Blueprint del panel de administración de plataforma."""
from __future__ import annotations

from flask import Blueprint, jsonify, render_template, redirect, url_for, request, flash

from app.core.auth_guard import login_required, role_required
from app.repositories.empresas import EmpresasRepository
from app.repositories.usuarios import UsuariosRepository
from app.repositories.restaurantes import RestaurantesRepository
from app.blueprints.workspace import actor, workspace_errors, WorkspaceError
from app.db.repository import shared_transaction

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


@bp.get('/moderaciones')
@workspace_errors
@login_required
@role_required('admin')
def moderations():
    return render_template('admin/moderations.html', restaurants=RestaurantesRepository.list_pending_review())


@bp.post('/moderaciones/<int:restaurant_id>/aprobar')
@workspace_errors
@login_required
@role_required('admin')
def approve_restaurant(restaurant_id):
    from app.repositories.auditoria import EventosAuditoriaRepository
    with shared_transaction():
        restaurant = RestaurantesRepository.approve_and_publish(restaurant_id)
        if not restaurant:
            raise WorkspaceError('El restaurante no está pendiente o está bloqueado; actualiza la lista.', 409)
        EventosAuditoriaRepository.record(accion='restaurante.aprobar_publicar', tipo_recurso='restaurante',
            id_usuario_actor=actor()['id'], id_empresa=restaurant.get('id_empresa'),
            id_recurso=str(restaurant_id), id_solicitud=getattr(request, 'request_id', None))
    flash('Restaurante aprobado y publicado.', 'success')
    return redirect(url_for('admin.moderations'))
