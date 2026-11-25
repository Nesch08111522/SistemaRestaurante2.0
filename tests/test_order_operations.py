from unittest.mock import Mock
from tests.test_qa_regression import app, data, sign_in
from app.models.order import OrderModel
from app.models.restaurant import RestaurantModel
from app.services import commerce


def test_owner_orders_are_limited_to_company_restaurant(app,data,monkeypatch):
    data[0]['rol'] = 'business_owner'
    monkeypatch.setattr('app.models.company.get_company_for_user', lambda *a: {'id_empresa':1})
    monkeypatch.setattr(RestaurantModel,'list_by_empresa',lambda *a:[{'id_restaurante':1,'nombre':'QA'}])
    rows=Mock(return_value=[]);monkeypatch.setattr(OrderModel,'list_by_restaurante',rows)
    with app.test_client() as c:
        sign_in(c); assert c.get('/owner/pedidos?restaurante_id=2').status_code==404
        assert c.get('/owner/pedidos?restaurante_id=1').status_code==200
    rows.assert_called_once_with(1,limit=101)


def test_business_transition_uses_expected_state_and_actor(app,data,monkeypatch):
    data[0]['rol'] = 'business_owner'
    monkeypatch.setattr('app.models.company.get_company_for_user', lambda *a: {'id_empresa':1})
    change=Mock(return_value={'estado':'accepted'});monkeypatch.setattr(commerce,'change_status',change)
    with app.test_client() as c:
        sign_in(c)
        assert c.post('/owner/api/pedidos/8/estado',json={'target':'accepted','expected_state':'pending'}).status_code==200
        assert c.post('/owner/api/pedidos/8/estado',json={'target':'accepted','expected_state':'pending','id_usuario':2}).status_code==400
    assert change.call_args.args[0]['id']==1
    assert change.call_args.args[1:]==(8,'accepted','pending')


def test_kitchen_state_route_does_not_accept_client_restaurant_id(app,data,monkeypatch):
    data[0]['rol'] = 'kitchen'
    monkeypatch.setattr('app.models.company.get_company_for_user', lambda *a: {'id_empresa':1})
    change=Mock(return_value={'estado':'preparing'});monkeypatch.setattr(commerce,'change_status',change)
    with app.test_client() as c:
        sign_in(c)
        assert c.post('/kitchen/api/pedidos/8/estado',json={'target':'preparing','expected_state':'accepted','restaurant_id':2}).status_code==400
    change.assert_not_called()
