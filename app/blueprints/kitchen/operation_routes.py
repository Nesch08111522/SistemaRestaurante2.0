"""Kitchen board and state changes backed by the transactional order service."""
from flask import jsonify, render_template
from app.core.auth_guard import empresa_required, login_required, role_required
from app.models.order import OrderModel
from app.models.restaurant import RestaurantModel
from app.services import commerce
from app.blueprints.workspace import actor, body, workspace_errors, WorkspaceError
from . import bp


@bp.get("/tablero")
@workspace_errors
@login_required
@empresa_required
@role_required("business_owner", "business_admin", "manager", "kitchen")
def board():
    from flask import g
    restaurant_ids = {r["id_restaurante"] for r in RestaurantModel.list_by_empresa(g.empresa["id_empresa"])}
    orders = []
    for rid in restaurant_ids:
        orders.extend(OrderModel.list_by_restaurante(rid, limit=100))
    active = [order for order in orders if order.get("estado") in {"accepted", "preparing", "ready"}]
    return render_template("workspace/kitchen.html", orders=sorted(active, key=lambda x: x.get("creado_en") or ""))


@bp.post("/api/pedidos/<int:order_id>/estado")
@workspace_errors
@login_required
@empresa_required
@role_required("business_owner", "business_admin", "manager", "kitchen")
def change_order_status(order_id):
    data = body({"target", "expected_state"})
    target, expected = data.get("target"), data.get("expected_state")
    if not isinstance(target, str) or not isinstance(expected, str):
        raise WorkspaceError("Indica el estado actual y el siguiente estado.")
    order = commerce.change_status(actor(), order_id, target, expected)
    return jsonify(success=True, state=order["estado"], message="Estado del pedido actualizado.")
