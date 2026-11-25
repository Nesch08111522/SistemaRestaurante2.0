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
