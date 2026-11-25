"""Private order consultation; public market routes remain unchanged."""
from flask import render_template
from app.core.auth_guard import login_required
from app.models.order import OrderModel
from app.blueprints.workspace import actor, WorkspaceError, workspace_errors
from . import bp


@bp.get('/pedidos')
@workspace_errors
@login_required
def orders():
    rows = OrderModel.list_by_usuario(actor()['id'], limit=101)
    return render_template('workspace/orders.html', orders=rows[:100], truncated=len(rows)>100, business=False)


@bp.get('/pedidos/<int:order_id>')
@workspace_errors
@login_required
def order_detail(order_id):
    order = OrderModel.get_by_id(order_id, full=False)
    if not order or order.get('id_usuario') != actor()['id']:
        raise WorkspaceError('Pedido no encontrado.', 404)
    detail = OrderModel.get_by_id(order_id, full=True)
    if not detail:
        raise WorkspaceError('Pedido no encontrado.', 404)
    return render_template('workspace/order_detail.html', order=detail, business=False)
