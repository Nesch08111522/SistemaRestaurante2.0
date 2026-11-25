"""Offline unit/HTTP tests. Providers, Storage and DB mocked ONLY in this test module."""
import io
import json
import struct
import uuid
from contextlib import nullcontext
from datetime import datetime, timezone
from unittest.mock import Mock
import pytest
import requests
from PIL import Image
from app import create_app
from app.services import menu3d as service
from app.services import menu3d_worker as worker
from app.repositories.menu3d import Menu3DRepository as Repo
from app.services.menu3d_validation import image_bytes, validate_glb, dish_payload, MAX_IMAGE
from app.services.menu3d_storage import IntegrationError, Storage
from app.ai.image_to_3d import MeshyProvider


def photo(fmt='JPEG',size=(100,100)):
    out=io.BytesIO();Image.new('RGB',size,'green').save(out,fmt);return out.getvalue()


def glb(change=None):
    doc={'asset':{'version':'2.0'},'buffers':[{'byteLength':36}],
        'bufferViews':[{'buffer':0,'byteLength':36}],
        'accessors':[{'bufferView':0,'componentType':5126,'count':3,'type':'VEC3'}],
        'meshes':[{'primitives':[{'attributes':{'POSITION':0}}]}],
        'nodes':[{'mesh':0}],'scenes':[{'nodes':[0]}],'scene':0}
    if change: change(doc)
    data=json.dumps(doc).encode();data+=b' '*((-len(data))%4)
    binary=struct.pack('<9f',0,0,0,1,0,0,0,1,0)
    chunks=struct.pack('<II',len(data),0x4E4F534A)+data+struct.pack('<II',36,0x004E4942)+binary
    return struct.pack('<4sII',b'glTF',2,12+len(chunks))+chunks


@pytest.fixture(autouse=True)
def no_external(monkeypatch):
    monkeypatch.setattr('app.db.connection.psycopg.connect',Mock(side_effect=AssertionError('Real database forbidden in unit tests')))
    monkeypatch.setattr('requests.sessions.Session.request',Mock(side_effect=AssertionError('Real network forbidden in unit tests')))


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr('app.models.company.get_company_for_user',lambda *a:None)
    return create_app({'TESTING':True,'SECRET_KEY':'qa'*32,'WTF_CSRF_ENABLED':False})


@pytest.fixture
def authorized(monkeypatch):
    user={'id':7,'role':'business_owner'}
    for path in ['app.core.security.fresh_session_user','app.core.auth_guard.fresh_session_user',
                 'app.services.menu3d.fresh_session_user','app.blueprints.ar.fresh_session_user']:
        monkeypatch.setattr(path,lambda:user)
    restaurant={'id_restaurante':1,'id_empresa':10,'nombre':'SOLO PRUEBA','estado_publicacion':'published'}
    monkeypatch.setattr(service.RestaurantesRepository,'get_by_id',lambda rid:restaurant if rid==1 else {**restaurant,'id_restaurante':rid,'id_empresa':20})
    monkeypatch.setattr(service,'permitted',lambda u,e,p:e==10)
    monkeypatch.setattr('app.blueprints.ar.permitted',lambda u,e,p:e==10)
    monkeypatch.setattr(service.PlatosRepository,'get_by_id',lambda pid:{'id_plato':pid,'id_restaurante':1 if pid==1 else 2})
    return restaurant


@pytest.mark.parametrize('fmt',['JPEG','PNG','WEBP'])
def test_image_accepts_decodes_normalizes(fmt):
    data,ext=image_bytes(photo(fmt));assert data.startswith(b'\xff\xd8');assert ext==fmt.lower()
    with Image.open(io.BytesIO(data)) as im: assert im.size==(100,100) and not im.getexif()


@pytest.mark.parametrize('data',[b'',b'<svg onload="evil()"></svg>',b'bad.jpg',b'x'*(MAX_IMAGE+1),photo(size=(32,32)),photo('GIF')])
def test_image_rejects_invalid(data):
    with pytest.raises(ValueError): image_bytes(data)


def test_image_optimizes_large_dimensions():
    normalized,_=image_bytes(photo(size=(2400,1200)))
    with Image.open(io.BytesIO(normalized)) as im: assert im.size==(1600,800)


def test_glb_accepts_self_contained_mesh():
    assert validate_glb(glb())['asset']['version']=='2.0'


@pytest.mark.parametrize('change',[
    lambda d:d['buffers'][0].update(uri='https://attacker.invalid/a'),
    lambda d:d['bufferViews'][0].update(byteLength=9999),
    lambda d:d['accessors'][0].update(count=10000),
    lambda d:d['meshes'][0]['primitives'][0]['attributes'].update(POSITION=-1),
    lambda d:d['nodes'][0].update(children=[0]),
    lambda d:d.update(meshes=[]),
])
def test_glb_rejects_unsafe_structure(change):
    with pytest.raises(ValueError):validate_glb(glb(change))


@pytest.mark.parametrize('data,mime',[(b'bad','model/gltf-binary'),(glb()[:-1],'model/gltf-binary'),(glb(),'text/html')])
def test_glb_rejects_bad_header_length_mime(data,mime):
    with pytest.raises(ValueError):validate_glb(data,mime)


@pytest.mark.parametrize('price',['NaN','Infinity','-1','10.001','1000000',None])
def test_invalid_price(price):
    with pytest.raises(ValueError):dish_payload({'nombre':'Plato QA','precio':price})


def test_dish_validation():
    p=dish_payload({'nombre':' QA ','precio':'12.50','ingredientes':['a','a',' b ']})
    assert p['ingredientes']==['a','b'];assert str(p['precio'])=='12.50'
    with pytest.raises(ValueError):dish_payload({'nombre':'QA','precio':1,'esta_disponible':'false'})


@pytest.mark.parametrize('path,method',[
    ('/ar/api/gestion/restaurantes/1','get'),('/ar/api/gestion/platos/1/recursos','get'),
    ('/ar/api/gestion/recursos/1','get'),('/ar/api/gestion/recursos/1/generar','post'),
    ('/ar/api/gestion/recursos/1/revision','post'),('/ar/api/gestion/platos/1/publicacion','post'),
    ('/ar/api/gestion/platos/1/fotografias','post'),('/ar/api/gestion/restaurantes/1/platos','post')])
def test_private_requires_login(app,path,method):
    assert getattr(app.test_client(),method)(path).status_code==401


@pytest.mark.parametrize('path,method',[
    ('/ar/api/gestion/restaurantes/2','get'),('/ar/api/gestion/platos/2/recursos','get'),
    ('/ar/api/gestion/platos/2/publicacion','post'),('/ar/api/gestion/platos/2/fotografias','post'),
    ('/ar/api/gestion/restaurantes/2/platos','post'),('/ar/api/gestion/platos/2','put')])
def test_cross_company_denied(app,authorized,path,method):
    assert getattr(app.test_client(),method)(path,json={'id_empresa':10}).status_code==403


def test_foreign_resource_denied(app,authorized,monkeypatch):
    monkeypatch.setattr(Repo,'resource',lambda rid:{'id_restaurante':2})
    assert app.test_client().get('/ar/api/gestion/recursos/9').status_code==403
    assert app.test_client().post('/ar/api/gestion/recursos/9/generar',json={'confirmar_costo':True}).status_code==403


def test_csrf_protects_mutations(app,authorized):
    app.config['WTF_CSRF_ENABLED']=True
    response=app.test_client().post('/ar/api/gestion/platos/1/publicacion',json={'publicado':True})
    assert response.status_code==400 and response.json['code']=='csrf_invalid'


def test_unpublished_restaurant_hidden(app,monkeypatch):
    monkeypatch.setattr(service.RestaurantesRepository,'get_by_id',lambda rid:{'estado_publicacion':'draft'})
    assert app.test_client().get('/ar/api/restaurantes/1/menu').status_code==404


def test_public_model_absent_no_generic(app,authorized,monkeypatch):
    monkeypatch.setattr(Repo,'menu',lambda *a,**kw:([{'id_plato':1,'nombre':'QA','foto_recurso':8}],False))
    result=app.test_client().get('/ar/api/modelos/1')
    assert result.status_code==200;assert result.json['modelo_url'] is None
    assert '/ar/recursos/8/foto'==result.json['foto_url'];assert '.glb' not in result.text


def test_private_model_not_exposed(app,authorized,monkeypatch):
    monkeypatch.setattr(Repo,'resource',lambda rid:{'id_plato':1,'id_restaurante':1,'aprobado':False,'estado':'completado'})
    monkeypatch.setattr(Repo,'menu',lambda *a,**kw:([{'id_plato':1,'foto_recurso':1}],False))
    assert app.test_client().get('/ar/recursos/1/modelo').status_code==404


def test_unpublished_dish_hidden(app,authorized,monkeypatch):
    monkeypatch.setattr(Repo,'menu',lambda *a,**kw:([],False))
    assert app.test_client().get('/ar/api/platos/1').status_code==404


@pytest.mark.parametrize('args',['page=-1','page=x','max_precio=NaN','max_precio=-2'])
def test_public_filters_validate(app,authorized,args):
    assert app.test_client().get('/ar/api/restaurantes/1/menu?'+args).status_code==400


def test_templates_render_real_fields(app,authorized,monkeypatch):
    monkeypatch.setattr('app.blueprints.ar.MembresiasRepository.list_by_usuario',lambda uid:[{'id_empresa':10}])
    monkeypatch.setattr(service.RestaurantesRepository,'list_by_empresa',lambda eid:[authorized])
    for path in ['/ar/restaurantes/1','/ar/gestion']:
        response=app.test_client().get(path);assert response.status_code==200
        assert 'SOLO PRUEBA' in response.text
        assert 'menu3d.css' in response.text


@pytest.fixture
def operations(monkeypatch,authorized):
    monkeypatch.setattr(service,'shared_transaction',nullcontext)
    monkeypatch.setattr(Repo,'lock_company',Mock())
    monkeypatch.setattr(service,'audit',Mock())
    monkeypatch.setattr(Repo,'history',lambda pid:[])
    monkeypatch.setattr(Repo,'usage',lambda eid:{'solicitudes':0,'reservado':0})
    monkeypatch.setattr(service,'provider',Mock())
    storage=Mock();monkeypatch.setattr(service,'Storage',lambda:storage)
    monkeypatch.setattr(Repo,'update',lambda rid,**kw:{'id_recurso':rid,**kw})
    return storage


def test_upload_validates_before_storage(app,operations):
    with app.test_request_context():
        with pytest.raises(ValueError):service.upload(1,[io.BytesIO(b'not image')])
    operations.upload.assert_not_called()


def test_upload_records_paths_and_cleans_up_failure(app,operations,monkeypatch):
    monkeypatch.setattr(Repo,'insert_resource',Mock(side_effect=RuntimeError('db write failed')))
    with app.test_request_context():
        with pytest.raises(RuntimeError):service.upload(1,[io.BytesIO(photo())])
    assert operations.upload.call_count==2
    assert operations.upload.call_args.args[0].startswith('empresas/10/restaurantes/1/platos/1/procesadas/')
    operations.delete.assert_called_once()


def test_save_dish_reuses_existing_tables(app,operations,monkeypatch):
    insert=Mock(return_value={'id_plato':12});monkeypatch.setattr(service.PlatosRepository,'insert',insert)
    replacements=[]
    for repo in [service.PlatosIngredientesRepository,service.PlatosEtiquetasRepository,service.PlatosRestriccionesDieteticasRepository]:
        m=Mock();monkeypatch.setattr(repo,'replace_for',m);replacements.append(m)
    monkeypatch.setattr(service,'query',Mock())
    with app.test_request_context():result=service.save_dish(1,{'nombre':'QA','precio':'10.50','ingredientes':['Tomate']})
    assert result['id_plato']==12;assert insert.call_args.kwargs['id_restaurante']==1
    replacements[0].assert_called_once_with(12,['Tomate'])


def resource(**kw):
    return {'id_recurso':1,'id_plato':1,'id_restaurante':1,'id_empresa':10,'clave_idempotencia':None,
        'envio_iniciado':False,'tarea_externa':None,'estado':'pendiente','error_codigo':None,
        'intentos':0,'solicitado_en':datetime.now(timezone.utc),
        'fotografias':['empresas/10/restaurantes/1/platos/1/procesadas/qa.jpeg'],**kw}


def test_generation_requires_cost_confirmation(app,operations,monkeypatch):
    monkeypatch.setattr(Repo,'resource',lambda *a,**kw:resource())
    with app.test_request_context():
        with pytest.raises(ValueError):service.enqueue(1,{'confirmar_costo':False})


def test_generation_queues_without_provider_post_and_idempotent(app,operations,monkeypatch):
    key=uuid.uuid4();row=resource();monkeypatch.setattr(Repo,'resource',lambda *a,**kw:row)
    with app.test_request_context():
        result=service.enqueue(1,{'confirmar_costo':True,'clave_idempotencia':str(key)})
        assert result['estado']=='en_cola'
        row.update(estado='procesando',clave_idempotencia=key)
        assert service.enqueue(1,{'confirmar_costo':True,'clave_idempotencia':str(key)}) is row
    service.provider.return_value.submit.assert_not_called()


def test_uncertain_submission_cannot_regenerate(app,operations,monkeypatch):
    monkeypatch.setattr(Repo,'resource',lambda *a,**kw:resource(envio_iniciado=True,estado='fallido'))
    with app.test_request_context():
        from werkzeug.exceptions import Conflict
        with pytest.raises(Conflict):service.enqueue(1,{'confirmar_costo':True,'clave_idempotencia':str(uuid.uuid4())})


def test_generation_quota(app,operations,monkeypatch):
    monkeypatch.setattr(Repo,'resource',lambda *a,**kw:resource())
    monkeypatch.setattr(Repo,'usage',lambda eid:{'solicitudes':10})
    with app.test_request_context():
        from werkzeug.exceptions import TooManyRequests
        with pytest.raises(TooManyRequests):service.enqueue(1,{'confirmar_costo':True,'clave_idempotencia':str(uuid.uuid4())})


@pytest.fixture
def job(monkeypatch):
    row=resource(estado='en_cola');monkeypatch.setattr(Repo,'claim',lambda token:row.copy())
    changes=[];monkeypatch.setattr(Repo,'job_update',lambda rid,token,**fields:changes.append(fields))
    api=Mock();storage=Mock();monkeypatch.setattr(worker,'provider',lambda:api);monkeypatch.setattr(worker,'Storage',lambda:storage)
    api.submit.return_value='external-qa';api.status.return_value={'status':'IN_PROGRESS','progress':24}
    api.download.return_value=(glb(),'model/gltf-binary')
    return row,changes,api,storage


def test_worker_persists_external_id_before_poll(job):
    row,changes,api,storage=job;assert worker.process_one()
    assert changes[0]['envio_iniciado'] is True;assert changes[1]['tarea_externa']=='external-qa'
    assert changes[-1]['progreso']==24;assert changes[-1]['lease_token'] is None


def test_worker_completion_validates_and_stores_without_approval(job):
    row,changes,api,storage=job;api.status.return_value={'status':'SUCCEEDED','model_urls':{'glb':'https://assets.meshy.ai/qa.glb'}}
    worker.process_one();assert changes[-1]['estado']=='completado';assert 'aprobado' not in changes[-1]
    assert storage.upload.call_args.args[0].endswith('/modelos-3d/1.glb')


def test_worker_rejects_invalid_result(job):
    row,changes,api,storage=job;api.status.return_value={'status':'SUCCEEDED','model_urls':{'glb':'https://assets.meshy.ai/qa.glb'}}
    api.download.return_value=(b'broken','model/gltf-binary');worker.process_one()
    assert changes[-1]['estado']=='rechazado';storage.upload.assert_not_called()


def test_worker_recovers_poll_without_resubmitting(job):
    row,changes,api,storage=job;row.update(tarea_externa='existing',envio_iniciado=True)
    api.status.side_effect=IntegrationError('temporary');worker.process_one()
    api.submit.assert_not_called();assert changes[-1]['intentos']==1;assert changes[-1]['estado']=='procesando'


def test_worker_interrupted_post_does_not_charge_again(job):
    row,changes,api,storage=job;row.update(envio_iniciado=True)
    worker.process_one();api.submit.assert_not_called();assert changes[-1]['error_codigo']=='envio_incierto'


def test_worker_post_timeout_no_retry(job):
    row,changes,api,storage=job;api.submit.side_effect=IntegrationError('uncertain')
    worker.process_one();assert api.submit.call_count==1;assert changes[-1]['estado']=='fallido'


@pytest.mark.parametrize('state',['FAILED','CANCELED'])
def test_provider_failure_not_published(job,state):
    row,changes,api,storage=job;api.status.return_value={'status':state};worker.process_one()
    assert changes[-1]['estado']=='fallido';storage.upload.assert_not_called()


def test_approve_requires_validated_model(app,operations,monkeypatch):
    monkeypatch.setattr(Repo,'resource',lambda *a,**kw:resource(estado='procesando'))
    with app.test_request_context():
        from werkzeug.exceptions import Conflict
        with pytest.raises(Conflict):service.review(1,True)


def test_meshy_contract_single_and_multi(monkeypatch):
    monkeypatch.setenv('MESHY_API_KEY','test-secret')
    response=Mock();response.json.return_value={'result':'task-1'}
    post=Mock(return_value=response);monkeypatch.setattr('requests.post',post)
    client=MeshyProvider();assert client.submit(['https://photo.invalid/1'])=='task-1'
    assert post.call_args.args[0].endswith('/image-to-3d');assert post.call_args.kwargs['json']['image_url'].endswith('/1')
    client.submit(['https://photo.invalid/1','https://photo.invalid/2'])
    assert post.call_args.args[0].endswith('/multi-image-to-3d');assert len(post.call_args.kwargs['json']['image_urls'])==2
    assert post.call_args.kwargs['allow_redirects'] is False


@pytest.mark.parametrize('url',['http://assets.meshy.ai/x','https://127.0.0.1/x','https://assets.meshy.ai.evil.test/x','https://user@assets.meshy.ai/x'])
def test_download_ssrf_blocked(monkeypatch,url):
    monkeypatch.setenv('MESHY_API_KEY','qa')
    with pytest.raises(ValueError):MeshyProvider().download(url)


def test_storage_path_and_contract(monkeypatch):
    monkeypatch.setenv('SUPABASE_URL','https://qa.supabase.co');monkeypatch.setenv('SUPABASE_SERVICE_ROLE_KEY','qa-secret')
    response=Mock(status_code=200);response.json.return_value={'signedURL':'/object/sign/platos-media/qa?token=qa'}
    send=Mock(return_value=response);monkeypatch.setattr('requests.request',send)
    storage=Storage();path='empresas/1/restaurantes/1/platos/1/procesadas/a.jpeg'
    assert storage.sign(path).startswith('https://qa.supabase.co/storage/v1/object/sign/')
    assert send.call_args.kwargs['json']=={'expiresIn':120}
    with pytest.raises(ValueError):storage.sign('../private')

def test_public_approved_model_redirects_only_after_publication(app,authorized,monkeypatch):
    monkeypatch.setattr(Repo,'resource',lambda rid:{'id_plato':1,'id_restaurante':1,'aprobado':True,'estado':'completado','modelo_path':'approved-path'})
    monkeypatch.setattr(Repo,'menu',lambda *a,**kw:([{'id_plato':1,'foto_recurso':1}],False))
    storage=Mock();storage.sign.return_value='https://qa.supabase.co/signed-approved'
    monkeypatch.setattr('app.blueprints.ar.Storage',lambda:storage)
    response=app.test_client().get('/ar/recursos/1/modelo')
    assert response.status_code==302 and response.headers['Location']=='https://qa.supabase.co/signed-approved'
    assert response.headers['Cache-Control']=='no-store'
    storage.sign.assert_called_once_with('approved-path')


def test_publication_and_approval_are_separate(app,operations,monkeypatch):
    publish=Mock(return_value={'publicado':True});approve=Mock(return_value={'aprobado':True})
    monkeypatch.setattr(Repo,'publish',publish);monkeypatch.setattr(Repo,'approve',approve)
    monkeypatch.setattr(Repo,'resource',lambda *a,**kw:resource(estado='completado',modelo_path='x',bytes_modelo=100))
    with app.test_request_context():
        assert service.review(1,True)['aprobado'];publish.assert_not_called()
        service.publish(1,True)
    publish.assert_called_once_with(1,True);approve.assert_called_once_with(1,1)


def test_regeneration_reuses_original_photos_without_paid_post(app,operations,monkeypatch):
    row=resource(estado='completado',bytes_fotos=200,originales=['original'])
    monkeypatch.setattr(Repo,'resource',lambda *a,**kw:row)
    insert=Mock(return_value={'id_recurso':2});monkeypatch.setattr(Repo,'insert_resource',insert)
    with app.test_request_context():assert service.regenerate(1)['id_recurso']==2
    assert insert.call_args.args[2]==['original'];operations.upload.assert_not_called();service.provider.assert_not_called()


def test_allegens_validated_not_inferred():
    result=dish_payload({'nombre':'QA','precio':'12','alergenos':['Maní']})
    assert result['alergenos']==['Maní']
    assert dish_payload({'nombre':'QA','precio':'12'})['alergenos']==[]
