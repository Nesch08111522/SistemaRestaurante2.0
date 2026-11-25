"""Business order monitoring. Public restaurant pages are intentionally untouched."""
from flask import jsonify, render_template, request
from app.core.auth_guard import empresa_required, login_required, role_required
from app.models.order import OrderModel
from app.models.restaurant import RestaurantModel
from app.services import commerce
from app.blueprints.workspace import actor, body, workspace_errors, WorkspaceError
from . import bp


def _restaurant_for_company():
    from flask import g
    restaurants = RestaurantModel.list_by_empresa(g.empresa["id_empresa"])
    raw = request.args.get("restaurante_id")
    try:
        selected_id = int(raw) if raw else (restaurants[0]["id_restaurante"] if restaurants else None)
    except (ValueError, TypeError):
        raise WorkspaceError("Restaurante inválido.")
    selected = next((item for item in restaurants if item["id_restaurante"] == selected_id), None)
    if raw and not selected:
        raise WorkspaceError("No puedes operar ese restaurante.", 404)
    return restaurants, selected


@bp.get("/pedidos")
@workspace_errors
@login_required
@empresa_required
@role_required("business_owner", "business_admin", "manager")
def orders():
    restaurants, selected = _restaurant_for_company()
    rows = OrderModel.list_by_restaurante(selected["id_restaurante"], limit=101) if selected else []
    return render_template("workspace/orders.html", orders=rows[:100], truncated=len(rows) > 100,
                           business=True, restaurants=restaurants,
                           restaurant_id=selected["id_restaurante"] if selected else None)


@bp.get("/pedidos/<int:order_id>")
@workspace_errors
@login_required
@empresa_required
@role_required("business_owner", "business_admin", "manager")
def order_detail(order_id):
    order = OrderModel.get_by_id(order_id, full=False)
    if not order:
        raise WorkspaceError("Pedido no encontrado.", 404)
    commerce.authorize(actor(), order["id_restaurante"], "orders.read.business")
    detail = OrderModel.get_by_id(order_id, full=True)
    return render_template("workspace/order_detail.html", order=detail, business=True)


@bp.post("/api/pedidos/<int:order_id>/estado")
@workspace_errors
@login_required
@empresa_required
@role_required("business_owner", "business_admin", "manager")
def change_order_status(order_id):
    data = body({"target", "expected_state"})
    target, expected = data.get("target"), data.get("expected_state")
    if not isinstance(target, str) or not isinstance(expected, str):
        raise WorkspaceError("Indica el estado actual y el siguiente estado.")
    order = commerce.change_status(actor(), order_id, target, expected)
    return jsonify(success=True, state=order["estado"], message="Estado del pedido actualizado.")
