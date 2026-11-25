import re
from pathlib import Path

import pytest
from flask import request
from tests.test_qa_regression import app, data, sign_in


@pytest.mark.parametrize('state,paid,targets', [
    ('pending', False, {'accepted', 'cancelled'}),
    ('pending', True, {'accepted'}),
    ('accepted', False, {'preparing', 'cancelled'}),
    ('preparing', False, {'ready'}),
    ('ready', False, {'delivered'}),
    ('delivered', True, set()),
    ('cancelled', False, set()),
])
def test_business_detail_exposes_valid_actions(app, data, monkeypatch, state, paid, targets):
    data[0]['rol'] = 'business_owner'
    order = dict(id_pedido=8, id_restaurante=1, estado=state, pagado=paid,
                 total=12, lineas=[], historial=[])
    monkeypatch.setattr('app.models.order.OrderModel.get_by_id', lambda *a, **k: order)
    monkeypatch.setattr('app.services.commerce.authorize', lambda *a: None)
    with app.test_client() as client:
        sign_in(client)
        response = client.get('/owner/pedidos/8')
        assert response.status_code == 200
        assert set(re.findall(r'data-target="([^"]+)"', response.text)) == targets
        assert 'workspace-order-actions.js' in response.text
        assert 'data-endpoint="/owner/api/pedidos/8/estado"' in response.text or not targets


def test_kitchen_shortcut_opens_operational_board(app, data, monkeypatch):
    data[0]['rol'] = 'business_owner'
    monkeypatch.setattr('app.models.order.OrderModel.list_by_restaurante', lambda *a, **k: [
        dict(id_pedido=8, estado='accepted')])
    with app.test_client() as client:
        sign_in(client)
        assert 'href="/kitchen/tablero"' in client.get('/auth/inicio').text
        response = client.get('/kitchen/tablero')
        assert response.status_code == 200
        assert 'data-target="preparing"' in response.text
        assert 'data-endpoint="/kitchen/api/pedidos/8/estado"' in response.text


def test_refresh_preserves_selected_restaurant(app, data, monkeypatch):
    data[0]['rol'] = 'business_owner'
    monkeypatch.setattr('app.models.restaurant.RestaurantModel.list_by_empresa',
                        lambda *a: [dict(id_restaurante=1), dict(id_restaurante=2)])
    monkeypatch.setattr('app.models.order.OrderModel.list_by_restaurante', lambda *a, **k: [])
    with app.test_client() as client:
        sign_in(client)
        response = client.get('/owner/pedidos?restaurante_id=2')
        assert response.status_code == 200
        assert 'href="/owner/pedidos?restaurante_id=2">Actualizar' in response.text


def test_upload_limit_is_per_request_and_enforced(app):
    app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024
    with app.test_request_context('/ar/api/gestion/platos/1/fotografias', method='POST'):
        assert request.max_content_length == 9 * 1024 * 1024
    with app.test_request_context('/'):
        assert request.max_content_length == 20 * 1024 * 1024
    response = app.test_client().post('/ar/api/gestion/platos/1/fotografias',
        data=b'x' * (9 * 1024 * 1024 + 1))
    # Authentication may reject before reading, but must never raise a server error.
    assert response.status_code in {401, 413}


def test_workspace_templates_have_no_duplicate_blocks(app):
    for name in ['workspace/order_detail.html', 'owner/dashboard.html', 'ar/manage.html',
                 'salon/index.html', 'kitchen/index.html']:
        app.jinja_env.get_template(name)
