from unittest.mock import Mock
import pytest
from app.services.business_registration import parse
from app.blueprints.workspace import WorkspaceError
from tests.test_qa_regression import app, data, sign_in

BASE={'restaurante':'Mi local','direccion':'Calle 1','distrito':'Lima'}

@pytest.mark.parametrize('extra', [{'precio_promedio':'NaN'},{'precio_promedio':'-1'}, {'precio_promedio':'1.001'}, {'latitud':'100','longitud':'0'}, {'latitud':'2'}, {'modalidad_servicio':'invalid'}, {'url_imagen':'javascript:alert(1)'}, {'hora_apertura':'25:00'}, {'hora_apertura':'09:00'}, {'tipo_menu':'x'}, {'id_categoria':'-1'}])
def test_invalid_fields(extra):
    with pytest.raises(WorkspaceError): parse(BASE|extra)

def test_privacy_discards_address_and_pin():
    fields,_=parse(BASE|{'solo_distrito':'on','latitud':'-8','longitud':'-79'})
    assert fields['direccion'] is None
    assert fields['latitud'] is None
    assert fields['longitud'] is None

def test_full_fields_and_overnight_hours():
    fields,lists=parse(BASE|{'hora_apertura':'18:00','hora_cierre':'02:00','precio_promedio':'35.50','etiquetas':'Criollo, Familiar, Criollo','modalidad_servicio':'dine_in_and_delivery','url_imagen':'https://example.com/photo.jpg'})
    assert str(fields['precio_promedio'])=='35.50'
    assert fields['hora_cierre'].hour==2
    assert lists['etiquetas']==['Criollo','Familiar']

def test_setup_render_and_preserved_error(app,data,monkeypatch):
    data[0]['rol']='business_owner'
    monkeypatch.setattr('app.models.company.get_company_for_user',lambda *a:None)
    with app.test_client() as c:
        sign_in(c)
        page=c.get('/owner/')
        assert page.status_code==200
        for name in ['modalidad_servicio','url_imagen','hora_apertura','latitud','etiquetas','business-map']:
            assert name in page.text
        response=c.post('/owner/registrar',data=BASE|{'empresa':'Mi empresa','precio_promedio':'-1'})
        assert response.status_code==400
        assert 'value="Mi local"' in response.text
        assert 'registration-error' in response.text


def test_registration_uses_maplibre_and_openfreemap_styles(app, data, monkeypatch):
    data[0]['rol'] = 'business_owner'
    monkeypatch.setattr('app.models.company.get_company_for_user', lambda *a: None)
    with app.test_client() as client:
        sign_in(client)
        response = client.get('/owner/')
    assert 'vendor/maplibre/maplibre-gl.css' in response.text
    assert 'vendor/maplibre/maplibre-gl.js' in response.text
    source = open('app/static/js/business-registration.js', encoding='utf-8').read()
    assert 'tiles.openfreemap.org/styles/liberty' in source
    assert 'tiles.openfreemap.org/styles/positron' in source
    assert 'maplibregl.Map' in source

def test_edit_other_company_denied(app,data,monkeypatch):
    data[0]['rol']='business_owner'
    monkeypatch.setattr('app.blueprints.owner.business_routes.RestaurantesRepository.get_by_id',lambda *a:{'id_empresa':99})
    with app.test_client() as c:
        sign_in(c)
        assert c.get('/owner/restaurantes/9/editar').status_code==404
        assert c.post('/owner/restaurantes/9/editar',data=BASE).status_code==404

def test_edit_ignores_ownership_and_publication_inputs(app,data,monkeypatch):
    from contextlib import nullcontext
    from app.blueprints.owner import business_routes as routes
    data[0]['rol']='business_owner'
    monkeypatch.setattr(routes.RestaurantesRepository,'get_by_id',lambda *a:{'id_empresa':1,'nombre':'Local','id_restaurante':1})
    monkeypatch.setattr(routes,'permitted',lambda *a:True)
    monkeypatch.setattr(routes,'shared_transaction',nullcontext)
    update=Mock()
    monkeypatch.setattr(routes.RestaurantesRepository,'update_fields',update)
    with app.test_client() as c:
        sign_in(c)
        response=c.post('/owner/restaurantes/1/editar',data=BASE|{'id_empresa':'99','estado_publicacion':'published','id_propietario':'99'})
        assert response.status_code==303
    fields=update.call_args.args[1]
    assert not {'id_empresa','id_propietario','estado_publicacion'} & fields.keys()
