from unittest.mock import Mock
from tests.test_qa_regression import app, data, sign_in
from app.models.order import OrderModel

def test_order_list_is_actor_scoped(app,data,monkeypatch):
    listing=Mock(return_value=[]);monkeypatch.setattr(OrderModel,'list_by_usuario',listing)
    with app.test_client() as c:
        sign_in(c);assert c.get('/mercado/pedidos?id_usuario=2').status_code==200
    listing.assert_called_once_with(1,limit=101)

def test_order_detail_checks_owner_before_reading_lines_and_address(app,data,monkeypatch):
    get=Mock(return_value={'id_pedido':8,'id_usuario':2})
    monkeypatch.setattr(OrderModel,'get_by_id',get)
    with app.test_client() as c:
        sign_in(c);assert c.get('/mercado/pedidos/8').status_code==404
    get.assert_called_once_with(8,full=False)

def test_order_detail_renders_real_values(app,data,monkeypatch):
    order={'id_pedido':8,'id_usuario':1,'id_restaurante':1,'estado':'pending','total':25.5,'lineas':[{'nombre_snapshot':'Almuerzo','cantidad':1,'precio_unitario':25.5}],'historial':[],'destino':None}
    monkeypatch.setattr(OrderModel,'get_by_id',lambda *a,**k:order)
    with app.test_client() as c:
        sign_in(c);response=c.get('/mercado/pedidos/8')
        assert response.status_code==200
        assert '25.50' in response.text and 'Almuerzo' in response.text
