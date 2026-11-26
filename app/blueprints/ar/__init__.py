"""Public menus and tenant-scoped administration; the existing /ar URLs stay valid."""
import math
from flask import Blueprint, abort, jsonify, redirect, render_template, request, url_for
from werkzeug.exceptions import HTTPException
from psycopg.errors import UndefinedTable, UniqueViolation
from app.core.auth_guard import login_required
from app.core.security import fresh_session_user
from app.models.company import permitted
from app.repositories.restaurantes import RestaurantesRepository
from app.repositories.membresias import MembresiasRepository
from app.repositories.platos import PlatosRepository
from app.repositories.menu3d import Menu3DRepository as Repo
from app.services import menu3d as service
from app.services.menu3d_storage import Storage, IntegrationError

bp = Blueprint('ar',__name__)



@bp.errorhandler(ValueError)
def invalid(error):
    return jsonify(success=False,error=str(error),code='invalid_input'),400


@bp.errorhandler(IntegrationError)
def integration_error(error):
    return jsonify(success=False,error=str(error),code='integration_unavailable'),503


@bp.errorhandler(UndefinedTable)
def migration_missing(error):
    return jsonify(success=False,error='Menú 3D requiere aplicar la migración de base de datos.',code='migration_required'),503


@bp.errorhandler(UniqueViolation)
def conflict(error):
    return jsonify(success=False,error='Ya existe una solicitud equivalente o una generación en curso.',code='conflict'),409


@bp.errorhandler(HTTPException)
def http_error(error):
    return jsonify(success=False,error=error.description,code=error.name),error.code


def filters():
    try:
        page = int(request.args.get('page',1))
        price = float(request.args['max_precio']) if request.args.get('max_precio') else None
        if not 1 <= page <= 10000 or price is not None and (not math.isfinite(price) or price<0): raise ValueError()
    except (ValueError,TypeError): raise ValueError('Página o precio inválido.') from None
    return dict(q=request.args.get('q',''),categoria=request.args.get('categoria',''),max_precio=price,
        disponible=request.args.get('disponible')=='1',recomendado=request.args.get('recomendado')=='1',
        orden=request.args.get('orden','nombre'),limit=24,offset=(page-1)*24)


def dish_json(row,private=False):
    result = {k:row.get(k) for k in ('id_plato','nombre','descripcion','precio','categoria','esta_disponible',
        'es_recomendado','ingredientes','etiquetas','restricciones_dieteticas','info_nutricional',
        'tiempo_preparacion_minutos','nivel_picante','publicado','alergenos')}
    endpoint = 'ar.private_asset' if private else 'ar.public_asset'
    result['foto_url'] = url_for(endpoint,resource_id=row['foto_recurso'],kind='foto') if row.get('foto_recurso') else None
    result['modelo_url'] = url_for(endpoint,resource_id=row['modelo_recurso'],kind='modelo') if row.get('modelo_recurso') else None
    return result


def resource_json(row):
    data = {k:row.get(k) for k in ('id_recurso','id_plato','version','estado','progreso','intentos',
        'error_codigo','error_mensaje','aprobado','creado_en','finalizado_en')}
    data['foto_url'] = url_for('ar.private_asset',resource_id=row['id_recurso'],kind='foto')
    data['modelo_url'] = url_for('ar.private_asset',resource_id=row['id_recurso'],kind='modelo') if row.get('modelo_path') else None
    return data


@bp.get('/')
def index():
    restaurants = [r for r in RestaurantesRepository.list_published(limit=100) if not r.get('suspendido') and not r.get('rechazado')]
    return render_template('ar/index.html',restaurantes=restaurants)


@bp.get('/restaurantes/<int:rid>')
def menu(rid):
    return render_template('ar/menu.html',restaurante=service.public_restaurant(rid))


@bp.get('/api/restaurantes/<int:rid>/menu')
def public_menu(rid):
    service.public_restaurant(rid)
    rows,more = Repo.menu(rid,filters())
    return jsonify(success=True,platos=[dish_json(r) for r in rows],hay_mas=more)


@bp.get('/api/restaurantes/<int:rid>/categorias')
def categories(rid):
    service.public_restaurant(rid)
    return jsonify(success=True,categorias=[r['categoria'] for r in Repo.categories(rid)])


@bp.get('/api/platos/<int:pid>')
def detail(pid):
    p = PlatosRepository.get_by_id(pid)
    if not p: abort(404)
    service.public_restaurant(p['id_restaurante'])
    rows,_ = Repo.menu(p['id_restaurante'],{'id_plato':pid})
    if not rows: abort(404)
    return jsonify(success=True,plato=dish_json(rows[0]))


@bp.get('/api/modelos/<int:id_plato>')
def api_modelo(id_plato):
    response = detail(id_plato).get_json()
    return jsonify(success=True,id_plato=id_plato,nombre=response['plato']['nombre'],
        modelo_url=response['plato']['modelo_url'],foto_url=response['plato']['foto_url'],
        nota='Representación aproximada generada desde fotografías.' if response['plato']['modelo_url'] else 'Modelo 3D todavía no disponible.')


@bp.get('/recursos/<int:resource_id>/<kind>')
def public_asset(resource_id,kind):
    row = Repo.resource(resource_id)
    if not row: abort(404)
    service.public_restaurant(row['id_restaurante'])
    dishes,_ = Repo.menu(row['id_restaurante'],{'id_plato':row['id_plato']})
    if not dishes: abort(404)
    if kind=='modelo' and (not row['aprobado'] or row['estado']!='completado'): abort(404)
    if kind=='foto' and dishes[0]['foto_recurso']!=resource_id: abort(404)
    return asset(row,kind)


def asset(row,kind):
    if kind not in ('foto','modelo'): abort(404)
    path = row['fotografias'][0] if kind=='foto' else row['modelo_path']
    if not path: abort(404)
    return redirect(Storage().sign(path),code=302)


@bp.get('/gestion')
@login_required
def manage():
    user = fresh_session_user()
    restaurants = []
    for membership in MembresiasRepository.list_by_usuario(user['id']):
        if permitted(user,membership['id_empresa'],'catalog.manage'):
            restaurants.extend(RestaurantesRepository.list_by_empresa(membership['id_empresa']))
    return render_template('ar/manage.html',restaurantes=restaurants)


@bp.get('/api/gestion/restaurantes/<int:rid>')
@login_required
def managed_menu(rid):
    restaurant,user = service.authorize(rid)
    rows,more = Repo.menu(rid,filters(),private=True)
    return jsonify(success=True,platos=[dish_json(r,True) for r in rows],hay_mas=more,
        resumen=Repo.stats(rid),puede_generar=permitted(user,restaurant['id_empresa'],'ai.business'))


@bp.post('/api/gestion/restaurantes/<int:rid>/platos')
@login_required
def create_dish(rid):
    dish = service.save_dish(rid,request.get_json(silent=True))
    return jsonify(success=True,id_plato=dish['id_plato']),201


@bp.put('/api/gestion/platos/<int:pid>')
@login_required
def edit_dish(pid):
    dish,_,_ = service.owned_dish(pid)
    service.save_dish(dish['id_restaurante'],request.get_json(silent=True),pid)
    return jsonify(success=True)


@bp.post('/api/gestion/platos/<int:pid>/fotografias')
@login_required
def upload(pid):
    return jsonify(success=True,recurso=resource_json(service.upload(pid,request.files.getlist('fotos')))),201


@bp.get('/api/gestion/platos/<int:pid>/recursos')
@login_required
def history(pid):
    service.owned_dish(pid)
    return jsonify(success=True,recursos=[resource_json(r) for r in Repo.history(pid)])


@bp.post('/api/gestion/recursos/<int:resource_id>/generar')
@bp.post('/api/gestion/recursos/<int:resource_id>/reintentar')
@login_required
def generate(resource_id):
    return jsonify(success=True,recurso=resource_json(service.enqueue(resource_id,request.get_json(silent=True)))),202


@bp.get('/api/gestion/recursos/<int:resource_id>')
@login_required
def status(resource_id):
    row,_,_ = service.owned_resource(resource_id)
    return jsonify(success=True,recurso=resource_json(row))


@bp.post('/api/gestion/recursos/<int:resource_id>/regenerar')
@login_required
def regenerate(resource_id):
    return jsonify(success=True,recurso=resource_json(service.regenerate(resource_id))),201


@bp.post('/api/gestion/recursos/<int:resource_id>/revision')
@login_required
def review(resource_id):
    body = request.get_json(silent=True)
    if not isinstance(body,dict): raise ValueError('Se requiere un objeto JSON.')
    return jsonify(success=True,recurso=resource_json(service.review(resource_id,body.get('aprobado'))))


@bp.post('/api/gestion/platos/<int:pid>/publicacion')
@login_required
def publish(pid):
    body = request.get_json(silent=True)
    if not isinstance(body,dict): raise ValueError('Se requiere un objeto JSON.')
    service.publish(pid,body.get('publicado'))
    return jsonify(success=True)


@bp.get('/gestion/recursos/<int:resource_id>/<kind>')
@login_required
def private_asset(resource_id,kind):
    row,_,_ = service.owned_resource(resource_id)
    return asset(row,kind)

from . import menu_import_routes
