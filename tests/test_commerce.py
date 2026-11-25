from contextlib import nullcontext
from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4
import pytest
from app.services import commerce as s
from app.services.errors import DomainError

@pytest.mark.parametrize('value',[True,'NaN','Infinity','-1','1.001',None])
def test_money_rejects_invalid_values(value):
    with pytest.raises(DomainError):s.money(value)

def test_money_is_exact():
    assert s.money('0.10')*3==Decimal('0.30')

@pytest.mark.parametrize('items',[[],[{'dish_id':True,'quantity':1}],[{'dish_id':1,'quantity':1,'price':0}],[{'dish_id':1,'quantity':1},{'dish_id':1,'quantity':2}]])
def test_cart_validation(items):
    with pytest.raises(DomainError):s.normalize_items(items)

@pytest.fixture
def commerce(monkeypatch):
    monkeypatch.setattr(s,'restaurant_transaction',lambda rid,*args:nullcontext())
    monkeypatch.setattr(s.PedidosMercadoRepository,'get_by_clave_solicitud',lambda key:None)
    monkeypatch.setattr(s.RestaurantModel,'get_by_id',lambda *a,**k:dict(id_restaurante=1,id_empresa=1,nombre='QA',estado_publicacion='published'))
    monkeypatch.setattr(s.Repo,'catalog',lambda rid:[dict(id_plato=2,nombre='QA',precio='12.50',stock=3)])
    create=Mock(return_value={'id_pedido':10});monkeypatch.setattr(s.OrderModel,'create',create)
    monkeypatch.setattr(s.Repo,'reserve',Mock(return_value=True));monkeypatch.setattr(s.Repo,'remember',Mock());monkeypatch.setattr(s.Repo,'event',Mock())
    return create,dict(restaurant_id=1,items=[{'dish_id':2,'quantity':2}],channel='Recojo',request_key=str(uuid4()),expected_total='25.00')

def test_checkout_uses_server_prices_and_actor(commerce):
    create,payload=commerce
    assert s.checkout({'id':7},payload)['id_pedido']==10
    kwargs=create.call_args.kwargs
    assert kwargs['total']==Decimal('25.00') and kwargs['id_usuario']==7
    s.Repo.reserve.assert_called_once_with(2,2,10,7)

def test_stale_total_cannot_create_order(commerce):
    create,payload=commerce;payload['expected_total']='1.00'
    with pytest.raises(DomainError,match='precio cambió'):s.checkout({'id':7},payload)
    create.assert_not_called()

def test_idempotency_rejects_changed_payload(commerce,monkeypatch):
    create,payload=commerce
    monkeypatch.setattr(s.PedidosMercadoRepository,'get_by_clave_solicitud',lambda key:dict(id_pedido=10,id_usuario=7,id_restaurante=1))
    monkeypatch.setattr(s.Repo,'control',lambda oid:{'hash_solicitud':'different'})
    with pytest.raises(DomainError,match='otro contenido'):s.checkout({'id':7},payload)
    create.assert_not_called()

def test_paid_order_cannot_be_cancelled_without_refund(monkeypatch):
    monkeypatch.setattr(s,'restaurant_transaction',lambda rid,*args:nullcontext())
    monkeypatch.setattr(s.OrderModel,'get_by_id',lambda *a,**k:dict(id_pedido=1,id_usuario=7,id_restaurante=1,estado='pending',pagado=True))
    monkeypatch.setattr(s.Repo,'control',lambda oid:dict(id_pedido=1))
    restore=Mock();monkeypatch.setattr(s.Repo,'restore',restore)
    with pytest.raises(DomainError,match='reembolso'):s.change_status({'id':7},1,'cancelled','pending',buyer=True)
    restore.assert_not_called()
