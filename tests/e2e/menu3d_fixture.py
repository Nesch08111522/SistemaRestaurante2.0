"""Local UI fixture ONLY. No production DB, provider, or account access.
Run: python -m tests.e2e.menu3d_fixture
"""
import io
from unittest.mock import patch, Mock
from flask import send_file
from PIL import Image
from app import create_app
from tests.test_menu3d import glb


def create_fixture():
    app=create_app({'TESTING':True,'SECRET_KEY':'ui-fixture-only-'*4,'WTF_CSRF_ENABLED':True})
    restaurant={'id_restaurante':1,'id_empresa':10,'nombre':'Restaurante de prueba · QA',
        'direccion':'Dirección de prueba','estado_publicacion':'published','url_imagen':None,'calificacion':None,
        'hora_apertura':None,'hora_cierre':None,'telefono':None,'distrito':'QA'}
    dishes=[{'id_plato':i,'nombre':f'Plato de prueba {i}', 'descripcion':'Datos ficticios exclusivos de esta prueba de interfaz.',
        'precio':10+i,'categoria':'Categoría QA '+str(i%2),'esta_disponible':i!=2,'es_recomendado':i==1,
        'ingredientes':['Ingrediente QA'],'restricciones_dieteticas':[],'etiquetas':['SOLO PRUEBAS'],
        'info_nutricional':None,'publicado':True,'foto_recurso':None,'modelo_recurso':1 if i==1 else None} for i in range(1,5)]
    def menu(rid,filters,**kw):
        rows=[d for d in dishes if (not filters.get('q') or filters['q'].lower() in d['nombre'].lower())
            and (not filters.get('categoria') or d['categoria']==filters['categoria'])
            and (not filters.get('recomendado') or d['es_recomendado'])
            and (not filters.get('disponible') or d['esta_disponible'])
            and (filters.get('max_precio') is None or d['precio']<=filters['max_precio'])]
        return rows,False
    patches={
        'app.db.connection.psycopg.connect':Mock(side_effect=AssertionError('DB forbidden in UI fixture')),
        'app.core.security.fresh_session_user':lambda:{'id':7,'role':'business_owner'},
        'app.core.auth_guard.fresh_session_user':lambda:{'id':7,'role':'business_owner'},
        'app.services.menu3d.fresh_session_user':lambda:{'id':7,'role':'business_owner'},
        'app.blueprints.ar.fresh_session_user':lambda:{'id':7,'role':'business_owner'},
        'app.models.company.get_company_for_user':lambda *a:None,
        'app.services.menu3d.permitted':lambda *a:True,
        'app.blueprints.ar.permitted':lambda *a:True,
        'app.repositories.restaurantes.RestaurantesRepository.get_by_id':lambda *a:restaurant,
        'app.repositories.restaurantes.RestaurantesRepository.list_by_empresa':lambda *a:[restaurant],
        'app.repositories.restaurantes.RestaurantesRepository.list_published':lambda **kw:[restaurant],
        'app.repositories.membresias.MembresiasRepository.list_by_usuario':lambda *a:[{'id_empresa':10}],
        'app.repositories.menu3d.Menu3DRepository.menu':menu,
        'app.repositories.menu3d.Menu3DRepository.categories':lambda *a,**kw:[{'categoria':'Categoría QA 0'},{'categoria':'Categoría QA 1'}],
        'app.repositories.menu3d.Menu3DRepository.stats':lambda *a:dict(total=4,publicados=4,generados=1,procesando=0,errores=0,sin_modelo=3),
        'app.repositories.menu3d.Menu3DRepository.resource':lambda *a,**kw:dict(id_recurso=1,id_plato=1,id_restaurante=1,aprobado=True,estado='completado',modelo_path='qa'),
        'app.repositories.menu3d.Menu3DRepository.history':lambda *a:[],
        'app.repositories.platos.PlatosRepository.get_by_id':lambda pid:{**dishes[pid-1],'id_restaurante':1},
        'app.services.menu3d_storage.Storage.sign':lambda *a:'/qa-test-model.glb',
        'app.services.menu3d_storage.Storage.__init__':lambda *a:None,
    }
    for target,value in patches.items():patch(target,value).start()
    @app.get('/qa-test-model.glb')
    def model():return send_file(io.BytesIO(glb()),mimetype='model/gltf-binary')
    return app


if __name__=='__main__':
    create_fixture().run(host='127.0.0.1',port=5093,debug=False,use_reloader=False)
