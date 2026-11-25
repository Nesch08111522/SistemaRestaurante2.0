"""Authenticated purchasing workspace; does not replace the public market."""
from flask import current_app, jsonify, render_template, request, url_for
from psycopg.errors import UndefinedTable, UndefinedColumn
from app.repositories.platos import PlatosRepository
from app.core.auth_guard import login_required
from app.models.restaurant import RestaurantModel
from app.services import commerce
from app.repositories.operations import OperationsRepository
from app.blueprints.workspace import actor, body, workspace_errors, WorkspaceError
from . import bp


@bp.get('/nuevo')
@workspace_errors
@login_required
def checkout():
    restaurants=[r for r in RestaurantModel.list_published(limit=100) if not r.get('suspendido') and not r.get('rechazado')]
    raw=request.args.get('restaurante_id')
    try: rid=int(raw) if raw else None
    except (ValueError,TypeError): raise WorkspaceError('Restaurante inválido.')
    selected=next((r for r in restaurants if r['id_restaurante']==rid),None)
    if raw and not selected: raise WorkspaceError('Restaurante no disponible.',404)
    dishes = []
    ordering_available = True
    if selected:
        try:
            dishes = OperationsRepository.catalog(rid)
        except (UndefinedTable, UndefinedColumn) as error:
            current_app.logger.warning('Checkout schema unavailable: %s', type(error).__name__)
            ordering_available = False
            dishes = PlatosRepository.list_by_restaurante(rid, only_available=True)
    return render_template('workspace/checkout.html', restaurants=restaurants,
                           restaurant=selected, dishes=dishes,
                           ordering_available=ordering_available)


@bp.post('/api/comprar')
@workspace_errors
@login_required
def buy():
    data=body({'restaurant_id','items','channel','request_key','expected_total','destination'})
    order=commerce.checkout(actor(),data)
    return jsonify(success=True,order_id=order['id_pedido'],url=url_for('market.order_detail',order_id=order['id_pedido'])),201


@bp.post('/api/pedidos/<int:order_id>/cancelar')
@workspace_errors
@login_required
def cancel_order(order_id):
    data=body({'expected_state'})
    expected=data.get('expected_state')
    if not isinstance(expected,str): raise WorkspaceError('Falta el estado esperado.')
    commerce.change_status(actor(),order_id,'cancelled',expected,buyer=True)
    return jsonify(success=True,message='Pedido cancelado; las porciones reservadas se devolvieron al stock.')
