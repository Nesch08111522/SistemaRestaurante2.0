from unittest.mock import Mock
from tests.test_qa_regression import app,data,sign_in
from app.services import commerce

def test_checkout_endpoint_rejects_client_identity_and_paid_flags(app,data,monkeypatch):
    buy=Mock();monkeypatch.setattr(commerce,'checkout',buy)
    with app.test_client() as c:
        sign_in(c)
        assert c.post('/mercado/api/comprar',json={'id_usuario':2,'pagado':True}).status_code==400
    buy.assert_not_called()

def test_checkout_endpoint_uses_authenticated_user(app,data,monkeypatch):
    buy=Mock(return_value={'id_pedido':1});monkeypatch.setattr(commerce,'checkout',buy)
    with app.test_client() as c:
        sign_in(c);r=c.post('/mercado/api/comprar',json={'items':[]})
        assert r.status_code==201 and r.json['url']=='/mercado/pedidos/1'
    assert buy.call_args.args[0]['id']==1

def test_checkout_requires_authentication(app):
    assert app.test_client().post('/mercado/api/comprar',json={}).status_code==401


def test_checkout_starts_with_business_selection(app, data, monkeypatch):
    catalog = Mock(side_effect=AssertionError('No catalog before choosing a restaurant'))
    monkeypatch.setattr('app.repositories.operations.OperationsRepository.catalog', catalog)
    with app.test_client() as c:
        sign_in(c)
        response = c.get('/mercado/nuevo')
        assert response.status_code == 200
        assert 'QA restaurante' in response.text
        assert 'restaurante_id=1' in response.text
        assert 'id="checkout-form"' not in response.text
    catalog.assert_not_called()


def test_checkout_missing_schema_keeps_menu_readable(app, data, monkeypatch):
    from psycopg.errors import UndefinedTable
    monkeypatch.setattr('app.repositories.operations.OperationsRepository.catalog',
                        Mock(side_effect=UndefinedTable('web_stock_platos')))
    listing = Mock(return_value=[{'id_plato': 3, 'nombre': 'Arroz con pollo', 'precio': 18}])
    monkeypatch.setattr('app.repositories.platos.PlatosRepository.list_by_restaurante', listing)
    with app.test_client() as c:
        sign_in(c)
        response = c.get('/mercado/nuevo?restaurante_id=1')
        assert response.status_code == 200
        assert 'Arroz con pollo' in response.text
        assert '18.00' in response.text
        assert 'Pedidos en línea aún no disponibles' in response.text
        assert 'Cambiar de negocio' in response.text
        assert 'id="checkout-form"' not in response.text
        assert 'Confirmar pedido' not in response.text
        assert 'SOLICITUD 503' not in response.text
    listing.assert_called_once_with(1, only_available=True)


def test_checkout_ready_schema_allows_ordering(app, data, monkeypatch):
    monkeypatch.setattr('app.repositories.operations.OperationsRepository.catalog',
                        lambda *a: [{'id_plato': 3, 'nombre': 'Arroz con pollo', 'precio': 18, 'stock': 5}])
    with app.test_client() as c:
        sign_in(c)
        response = c.get('/mercado/nuevo?restaurante_id=1')
        assert response.status_code == 200
        assert 'id="checkout-form"' in response.text
        assert 'Confirmar pedido' in response.text
        assert '5 porciones disponibles' in response.text


def test_checkout_no_businesses_has_clear_empty_state(app, data, monkeypatch):
    monkeypatch.setattr('app.models.restaurant.RestaurantModel.list_published', lambda **k: [])
    with app.test_client() as c:
        sign_in(c)
        response = c.get('/mercado/nuevo')
        assert response.status_code == 200
        assert 'Aún no hay negocios disponibles' in response.text
        assert 'id="checkout-form"' not in response.text


def test_checkout_invalid_or_unpublished_business_rejected(app, data, monkeypatch):
    catalog = Mock()
    monkeypatch.setattr('app.repositories.operations.OperationsRepository.catalog', catalog)
    with app.test_client() as c:
        sign_in(c)
        assert c.get('/mercado/nuevo?restaurante_id=invalid').status_code == 400
        assert c.get('/mercado/nuevo?restaurante_id=999').status_code == 404
    catalog.assert_not_called()
