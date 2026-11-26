"""Restaurant tables: create, occupy, release, clean and remove."""
from flask import Blueprint, g, jsonify, render_template
from app.core.auth_guard import empresa_required, login_required, role_required
from app.blueprints.workspace import actor, body, text, workspace_errors, WorkspaceError
from app.blueprints.owner.operation_routes import _restaurant_for_company
from app.models.company import permitted
from app.repositories.salon import SalonRepository as Repo
from app.services.commerce import integer

bp = Blueprint('salon', __name__)
STAFF = ('business_owner', 'business_admin', 'manager', 'cashier', 'waiter')


def selected(permission):
    restaurants, restaurant = _restaurant_for_company()
    if not restaurant:
        raise WorkspaceError('Primero registra un restaurante desde Mi empresa.', 409)
    if not permitted(actor(), g.empresa['id_empresa'], permission):
        raise WorkspaceError('Tu membresía o plan no permite esta acción en el salón.', 403)
    return restaurants, restaurant


@bp.get('/')
@workspace_errors
@login_required
@role_required(*STAFF)
@empresa_required
def index():
    restaurants, restaurant = _restaurant_for_company()
    return render_template('salon/index.html', restaurants=restaurants, restaurant=restaurant)


@bp.get('/api/mesas')
@workspace_errors
@login_required
@role_required(*STAFF)
@empresa_required
def api_mesas():
    _, restaurant = selected('tables.service')
    return jsonify(mesas=Repo.list_for(restaurant['id_restaurante']),
                   can_manage=permitted(actor(), g.empresa['id_empresa'], 'tables.manage'))


@bp.post('/api/mesas')
@workspace_errors
@login_required
@role_required(*STAFF)
@empresa_required
def create_table():
    _, restaurant = selected('tables.manage')
    data = body({'nombre','zona','capacidad'})
    row = Repo.create(restaurant['id_restaurante'], text(data.get('nombre'), 'nombre', 24, required=True),
                      text(data.get('zona') or 'General', 'zona', 40, required=True),
                      integer(data.get('capacidad'), 'Capacidad', 1, 40))
    return jsonify(success=True, mesa=row), 201


@bp.post('/api/mesas/<int:table_id>/estado')
@workspace_errors
@login_required
@role_required(*STAFF)
@empresa_required
def change_table(table_id):
    _, restaurant = selected('tables.service')
    data = body({'expected_state','target','personas'})
    expected, target = data.get('expected_state'), data.get('target')
    if not isinstance(expected, str) or not isinstance(target, str) or (expected, target) not in {('libre','ocupada'),('ocupada','limpieza'),('limpieza','libre')}:
        raise WorkspaceError('Cambio de estado no permitido.', 409)
    people = integer(data.get('personas'), 'Personas', 1, 40) if target == 'ocupada' else 0
    row = Repo.transition(restaurant['id_restaurante'], table_id, expected, target, people)
    if not row:
        raise WorkspaceError('La mesa cambió o la cantidad supera su capacidad. Actualiza el salón.', 409)
    return jsonify(success=True, mesa=row)


@bp.delete('/api/mesas/<int:table_id>')
@workspace_errors
@login_required
@role_required(*STAFF)
@empresa_required
def delete_table(table_id):
    _, restaurant = selected('tables.manage')
    body(set())
    if not Repo.delete(restaurant['id_restaurante'], table_id):
        raise WorkspaceError('Solo puedes eliminar una mesa libre de este restaurante.', 409)
    return jsonify(success=True)
