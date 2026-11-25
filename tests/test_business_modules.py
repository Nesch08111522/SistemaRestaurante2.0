from contextlib import contextmanager
from unittest.mock import MagicMock, Mock
import pytest
from tests.test_qa_regression import app, data, sign_in


@pytest.mark.parametrize('path', ['/owner/','/salon/','/kitchen/','/kitchen/tablero'])
def test_owner_without_company_can_reach_setup(app, data, monkeypatch, path):
    data[0]['rol'] = 'business_owner'
    monkeypatch.setattr('app.models.company.get_company_for_user', lambda *a: None)
    with app.test_client() as c:
        sign_in(c)
        response = c.get(path, follow_redirects=True)
        assert response.status_code == 200
        assert 'Registrar empresa y restaurante' in response.text


def test_company_selection_skips_invited_and_suspended(monkeypatch):
    from app.models.company import get_company_for_user
    monkeypatch.setattr('app.models.company.MembresiasRepository.list_by_usuario', lambda *a: [
        dict(id_empresa=1,estado='invited'), dict(id_empresa=2,estado='active'), dict(id_empresa=3,estado='active')])
    monkeypatch.setattr('app.models.company.EmpresasRepository.get_by_id', lambda i: dict(id_empresa=i,estado='active' if i==3 else 'suspended'))
    monkeypatch.setattr('app.models.company.EmpresasSuscripcionesRepository.get_by_empresa', lambda *a: {})
    monkeypatch.setattr('app.models.company.EmpresasSuscripcionesRepository.get_disabled_modules', lambda *a: [])
    monkeypatch.setattr('app.models.company.SucursalesRepository.list_by_empresa', lambda *a: [])
    assert get_company_for_user(1)['id_empresa'] == 3


@pytest.fixture
def salon(data, monkeypatch):
    data[0]['rol'] = 'business_owner'
    monkeypatch.setattr('app.blueprints.salon.permitted', lambda *a: True)
    from app.repositories.salon import SalonRepository
    monkeypatch.setattr(SalonRepository, 'list_for', lambda *a: [])
    return SalonRepository


def test_salon_load_and_create(app, salon, monkeypatch):
    create = Mock(return_value={'id_mesa':4})
    monkeypatch.setattr(salon, 'create', create)
    with app.test_client() as c:
        sign_in(c)
        assert c.get('/salon/').status_code == 200
        assert c.get('/salon/api/mesas?restaurante_id=1').json['mesas'] == []
        assert c.post('/salon/api/mesas?restaurante_id=1', json={'nombre':'Mesa 1','zona':'Terraza','capacidad':4}).status_code == 201
        create.assert_called_once_with(1,'Mesa 1','Terraza',4)


@pytest.mark.parametrize('payload', [dict(nombre='',capacidad=4),dict(nombre='1',capacidad=True),dict(nombre='1',capacidad=41),dict(nombre='1',capacidad=4,id_restaurante=2)])
def test_salon_rejects_invalid_create(app, salon, payload):
    with app.test_client() as c:
        sign_in(c)
        assert c.post('/salon/api/mesas',json=payload).status_code == 400


def test_salon_tenant_and_subscription_permissions(app, salon, monkeypatch):
    with app.test_client() as c:
        sign_in(c)
        assert c.get('/salon/api/mesas?restaurante_id=2').status_code == 404
        monkeypatch.setattr('app.blueprints.salon.permitted', lambda *a: False)
        assert c.post('/salon/api/mesas',json={'nombre':'1','capacidad':4}).status_code == 403


@pytest.mark.parametrize('expected,target,people', [('libre','ocupada',2),('ocupada','limpieza',0),('limpieza','libre',0)])
def test_table_lifecycle(app, salon, monkeypatch, expected, target, people):
    change = Mock(return_value={'estado':target})
    monkeypatch.setattr(salon,'transition',change)
    with app.test_client() as c:
        sign_in(c)
        assert c.post('/salon/api/mesas/4/estado',json={'expected_state':expected,'target':target,'personas':people}).status_code == 200
    change.assert_called_once_with(1,4,expected,target,people)


def test_stale_table_and_occupied_delete_return_conflict(app, salon, monkeypatch):
    monkeypatch.setattr(salon,'transition',lambda *a: None)
    monkeypatch.setattr(salon,'delete',lambda *a: None)
    with app.test_client() as c:
        sign_in(c)
        assert c.post('/salon/api/mesas/4/estado',json={'expected_state':'libre','target':'ocupada','personas':2}).status_code == 409
        assert c.delete('/salon/api/mesas/4',json={}).status_code == 409


def test_kitchen_legacy_url_opens_real_board(app,data):
    data[0]['rol']='business_owner'
    with app.test_client() as c:
        sign_in(c)
        response=c.get('/kitchen/')
        assert response.status_code==200
        assert 'Tablero de preparación' in response.text
        assert c.get('/kitchen/tablero?restaurante_id=2').status_code==404


def test_registration_is_atomic_and_ignores_client_plan(app,data,monkeypatch):
    data[0]['rol']='business_owner'
    from app.blueprints.owner import business_routes as routes
    connection=MagicMock()
    @contextmanager
    def transaction():
        yield connection
    monkeypatch.setattr(routes,'shared_transaction',transaction)
    monkeypatch.setattr(routes,'get_company_for_user',lambda *a: None)
    create=Mock(return_value={'id_empresa':12})
    monkeypatch.setattr(routes,'create_company_with_owner',create)
    restaurant=Mock()
    monkeypatch.setattr(routes.RestaurantesRepository,'insert',restaurant)
    with app.test_client() as c:
        sign_in(c)
        response=c.post('/owner/registrar',data={'empresa':'Mi empresa','restaurante':'Local','direccion':'Av. 1','distrito':'Lima','plan':'premium','id_propietario':'999'})
        assert response.status_code==303
    assert create.call_args.kwargs['owner_user_id']==1
    assert create.call_args.kwargs['plan']=='basic'
    assert restaurant.call_args.kwargs['id_empresa']==12
    assert restaurant.call_args.kwargs['id_propietario']==1


def test_diner_cannot_register_business(app,data):
    with app.test_client() as c:
        sign_in(c)
        assert c.post('/owner/registrar',data={}).status_code==403
