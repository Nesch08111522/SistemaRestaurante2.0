from io import BytesIO
from contextlib import contextmanager
from unittest.mock import Mock
import pytest
from openpyxl import load_workbook
from docx import Document
from app.services import menu_import as subject


def filled(fmt,price='25.50'):
    stream=subject.template(fmt);out=BytesIO()
    if fmt=='xlsx':
        book=load_workbook(stream);sheet=book['Platos'];sheet.cell(2,1,'Ceviche');sheet.cell(2,2,price);sheet.cell(2,5,'pescado; limón');book.save(out)
    else:
        doc=Document(stream);cells=doc.tables[0].rows[1].cells;cells[0].text='Ceviche';cells[1].text=price;cells[4].text='pescado; limón';doc.save(out)
    return out.getvalue()


@pytest.mark.parametrize('fmt',['xlsx','docx'])
def test_template_roundtrip(fmt):
    rows=subject.read_document(filled(fmt),'carta.'+fmt)
    assert rows[0]['nombre']=='Ceviche'
    assert rows[0]['precio']=='25.50'
    assert rows[0]['ingredientes']==['pescado','limón']
    assert rows[0]['alergenos']==[]


@pytest.mark.parametrize('price',['','NaN','-1','1.001','=1+1'])
def test_invalid_price(price):
    with pytest.raises(ValueError): subject.read_document(filled('xlsx',price),'carta.xlsx')


def test_invalid_and_empty_documents():
    for raw,name in [(b'bad','carta.docx'),(subject.template('xlsx').getvalue(),'carta.xlsx'),(b'x','carta.xls'),(b'x'*(subject.MAX_FILE+1),'carta.xlsx')]:
        with pytest.raises(ValueError): subject.read_document(raw,name)


def test_photo_missing_price_and_no_invention(monkeypatch):
    monkeypatch.setattr('app.ai.client.is_configured',lambda:True)
    monkeypatch.setattr(subject,'image_bytes',lambda raw:(b'image','jpeg'))
    monkeypatch.setattr('app.ai.client.call_json',lambda **kw:{'platos':[{'nombre':'Ceviche','precio':None}]})
    row=subject.read_photo(b'image',7)[0]
    assert row['precio'] is None and row['alergenos']==[]
    with pytest.raises(ValueError): subject.normalize(row)


def test_photo_no_mock_results(monkeypatch):
    monkeypatch.setattr('app.ai.client.is_configured',lambda:False)
    with pytest.raises(ValueError,match='configurar'): subject.read_photo(b'image',7)
    monkeypatch.setattr('app.ai.client.is_configured',lambda:True)
    monkeypatch.setattr(subject,'image_bytes',lambda raw:(b'image','jpeg'))
    monkeypatch.setattr('app.ai.client.call_json',lambda **kw:{'mock':True})
    with pytest.raises(ValueError,match='No se pudo'): subject.read_photo(b'image',7)


def test_batch_atomic_and_duplicates(monkeypatch):
    from app.services import menu3d
    saved=[]
    @contextmanager
    def transaction():
        try: yield
        except Exception: saved.clear();raise
    monkeypatch.setattr('app.db.repository.shared_transaction',transaction)
    monkeypatch.setattr(menu3d,'authorize',lambda rid:({'id_empresa':2},{'id':7}))
    monkeypatch.setattr('app.repositories.menu3d.Menu3DRepository.lock_company',lambda eid:None)
    monkeypatch.setattr('app.repositories.platos.PlatosRepository.list_by_restaurante',lambda rid:[{'nombre':'Existente'}])
    save=Mock(return_value={'id_plato':1});monkeypatch.setattr(menu3d,'save_dish',save)
    with pytest.raises(ValueError,match='repetido'):subject.save_batch(1,[{'nombre':'Existente','precio':1}])
    save.assert_not_called()
    with pytest.raises(ValueError,match='repetido'):subject.save_batch(1,[{'nombre':'Nuevo','precio':1},{'nombre':' NUEVO ','precio':2}])
    save.assert_not_called()
    def fail_second(rid,row):
        if saved:raise RuntimeError('database failed')
        saved.append(row);return {'id_plato':1}
    monkeypatch.setattr(menu3d,'save_dish',fail_second)
    with pytest.raises(RuntimeError):subject.save_batch(1,[{'nombre':'Uno','precio':1},{'nombre':'Dos','precio':2}])
    assert saved==[]


@pytest.fixture
def client(monkeypatch):
    from flask import Flask, abort
    from app.blueprints.ar import bp
    from app.services import menu3d
    app=Flask(__name__);app.config.update(TESTING=True,SECRET_KEY='test')
    app.register_blueprint(bp,url_prefix='/ar')
    monkeypatch.setattr('app.core.auth_guard.fresh_session_user',lambda:{'id':7})
    def authorize(rid,permission='catalog.manage'):
        if rid!=1:abort(403)
        return {'id_empresa':2},{'id':7}
    monkeypatch.setattr(menu3d,'authorize',authorize)
    monkeypatch.setattr('app.repositories.categorias_plato.CategoriasPlatoRepository.list_all',lambda:['Entrada','Fondo'])
    return app.test_client()


def test_http_preview_never_saves(client,monkeypatch):
    save=Mock();monkeypatch.setattr(subject,'save_batch',save)
    response=client.post('/ar/api/gestion/restaurantes/1/importar/analizar',data={'archivo':(BytesIO(filled('xlsx')),'menu.xlsx')})
    assert response.status_code==200 and response.json['platos'][0]['nombre']=='Ceviche'
    save.assert_not_called()
    assert response.json['categorias']==['Entrada','Fondo']
    assert client.get('/ar/api/gestion/restaurantes/1/plantilla/docx').status_code==200
    assert client.post('/ar/api/gestion/restaurantes/1/importar/guardar',json={'platos':[]}).status_code==400


@pytest.mark.parametrize('endpoint',['plantilla/xlsx','importar/analizar','importar/guardar'])
def test_http_tenant_and_login(client,monkeypatch,endpoint):
    method=client.get if endpoint.startswith('plantilla') else client.post
    assert method('/ar/api/gestion/restaurantes/2/'+endpoint).status_code==403
    monkeypatch.setattr('app.core.auth_guard.fresh_session_user',lambda:None)
    assert method('/ar/api/gestion/restaurantes/1/'+endpoint).status_code==401
