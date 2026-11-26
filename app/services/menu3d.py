"""Application operations, ownership derived from DB, transactional audit and quotas."""
import logging
import os
import uuid
from datetime import datetime, timezone
from flask import abort, request
from app.core.security import fresh_session_user
from app.models.company import permitted
from app.repositories.restaurantes import RestaurantesRepository
from app.repositories.platos import (PlatosRepository, PlatosIngredientesRepository,
    PlatosEtiquetasRepository, PlatosRestriccionesDieteticasRepository)
from app.repositories.menu3d import Menu3DRepository as Repo, query
from app.repositories.auditoria import EventosAuditoriaRepository
from app.db.repository import shared_transaction
from app.services.menu3d_storage import Storage
from app.services.menu3d_validation import image_bytes, dish_payload, MAX_IMAGE
from app.ai.image_to_3d import provider

logger = logging.getLogger(__name__)


def public_restaurant(rid):
    r = RestaurantesRepository.get_by_id(rid)
    if not r or r.get('estado_publicacion') != 'published' or r.get('suspendido') or r.get('rechazado'):
        abort(404)
    return r


def authorize(rid, permission='catalog.manage'):
    user = fresh_session_user()
    if not user: abort(401)
    restaurant = RestaurantesRepository.get_by_id(rid)
    if not restaurant: abort(404)
    if not restaurant.get('id_empresa') or not permitted(user, restaurant['id_empresa'], permission):
        abort(403, description='Tu membresía o suscripción no permite esta operación.')
    return restaurant, user


def owned_dish(pid, permission='catalog.manage'):
    dish = PlatosRepository.get_by_id(pid)
    if not dish: abort(404)
    restaurant, user = authorize(dish['id_restaurante'], permission)
    return dish, restaurant, user


def owned_resource(resource_id, permission='catalog.manage'):
    row = Repo.resource(resource_id)
    if not row: abort(404)
    restaurant, user = authorize(row['id_restaurante'], permission)
    return row, restaurant, user


def audit(action, eid, uid, resource_id):
    EventosAuditoriaRepository.record(accion='menu3d.'+action, tipo_recurso='menu3d',
        id_usuario_actor=uid, id_empresa=eid, id_recurso=str(resource_id),
        id_solicitud=getattr(request,'request_id',None))


def save_dish(rid, body, pid=None):
    r, user = authorize(rid)
    if pid:
        dish = PlatosRepository.get_by_id(pid)
        if not dish or dish['id_restaurante'] != rid: abort(404)
    data = dish_payload(body)
    # Empty optional categories must be SQL NULL, never an empty foreign key.
    if data['categoria']:
        from app.repositories.categorias_plato import CategoriasPlatoRepository
        categories = CategoriasPlatoRepository.list_all()
        canonical = next((name for name in categories if name.casefold() == data['categoria'].casefold()), None)
        if canonical is None:
            raise ValueError('Categoría no válida para ' + data['nombre'] + '. Selecciona: ' + ', '.join(categories) + ', o deja la categoría vacía.')
        data['categoria'] = canonical
    else:
        data['categoria'] = None
    ingredients = data.pop('ingredientes'); tags = data.pop('etiquetas'); restrictions = data.pop('restricciones_dieteticas')
    allergens = data.pop('alergenos')
    with shared_transaction():
        Repo.lock_company(r['id_empresa'])
        dish = PlatosRepository.update_fields(pid,data) if pid else PlatosRepository.insert(id_restaurante=rid, **data)
        pid = dish['id_plato']
        PlatosIngredientesRepository.replace_for(pid,ingredients)
        PlatosEtiquetasRepository.replace_for(pid,tags)
        PlatosRestriccionesDieteticasRepository.replace_for(pid,restrictions)
        query('''INSERT INTO public.platos_menu3d(id_plato,alergenos) VALUES(%s,%s)
            ON CONFLICT(id_plato) DO UPDATE SET alergenos=EXCLUDED.alergenos,actualizado_en=now()
            RETURNING id_plato''', (pid,allergens))
        # Keep legacy menu readers synchronized without replacing their existing order.
        query('''INSERT INTO public.restaurantes_platos(id_restaurante,posicion,id_plato)
            SELECT %s,COALESCE(MAX(posicion),0)+1,%s FROM public.restaurantes_platos WHERE id_restaurante=%s
            HAVING NOT EXISTS(SELECT 1 FROM public.restaurantes_platos WHERE id_restaurante=%s AND id_plato=%s)
            RETURNING id_plato''', (rid,pid,rid,rid,pid))
        audit('guardar_plato',r['id_empresa'],user['id'],pid)
    return dish


def upload(pid, files):
    dish,r,user = owned_dish(pid)
    if not 1 <= len(files) <= 4:
        raise ValueError('Selecciona de una a cuatro fotografías del mismo plato.')
    images = []
    for file in files:
        original = file.read(MAX_IMAGE+1)
        normalized, ext = image_bytes(original)
        images.append((original,normalized,ext))
    storage = Storage()
    size = sum(len(a)+len(b) for a,b,_ in images)
    prefix = f"empresas/{r['id_empresa']}/restaurantes/{dish['id_restaurante']}/platos/{pid}/"
    paths, photos, uploaded = [], [], []
    try:
        with shared_transaction():
            Repo.lock_company(r['id_empresa'])
            if len(Repo.history(pid)) >= 20:
                abort(409, description='Límite de 20 versiones por plato. Solicita archivar recursos antes de subir más.')
            if Repo.usage(r['id_empresa'])['reservado'] + size + 52428800 > int(os.getenv('MENU3D_COMPANY_BYTES','1073741824')):
                abort(409, description='Se alcanzó la cuota de almacenamiento de la empresa.')
            for original,normalized,ext in images:
                key = uuid.uuid4().hex
                path = prefix+'originales/'+key+'.'+ext
                photo = prefix+'procesadas/'+key+'.jpeg'
                uploaded.append(path); storage.upload(path, original, 'image/'+ext)
                uploaded.append(photo); storage.upload(photo, normalized, 'image/jpeg')
                paths.append(path); photos.append(photo)
            row = Repo.insert_resource(pid,user['id'],paths,photos,size)
            audit('subir_fotos',r['id_empresa'],user['id'],row['id_recurso'])
            return row
    except Exception:
        if uploaded:
            try: storage.delete(uploaded)
            except Exception: logger.error('menu3d: limpieza pendiente de %s objetos tras carga fallida',len(uploaded))
        raise


def enqueue(resource_id, body):
    row,r,user = owned_resource(resource_id,'ai.business')
    if not isinstance(body,dict) or body.get('confirmar_costo') is not True:
        raise ValueError('Confirma el posible costo del proveedor antes de continuar.')
    try: key = uuid.UUID(str(body.get('clave_idempotencia')))
    except (ValueError,TypeError): raise ValueError('La clave de idempotencia debe ser UUID.') from None
    provider(); Storage()  # Fail before enqueuing when credentials are missing.
    with shared_transaction():
        Repo.lock_company(r['id_empresa'])
        row = Repo.resource(resource_id,lock=True)
        if row['clave_idempotencia']:
            if str(row['clave_idempotencia']) == str(key): return row
            if row['estado'] != 'fallido' or row['error_codigo'] not in ('servicio_temporal','tiempo_agotado'):
                abort(409,description='Esta versión ya fue solicitada. Sube fotos para crear otra versión.')
        if row['envio_iniciado'] and not row['tarea_externa']:
            abort(409,description='Envío incierto: soporte debe recuperar la tarea desde Meshy antes de continuar.')
        if row['estado'] not in ('pendiente','fallido'):
            abort(409,description='La versión no admite otra solicitud.')
        if any(h['estado'] in ('en_cola','procesando') for h in Repo.history(row['id_plato'])):
            abort(409,description='Ya hay una generación en curso para este plato.')
        if not row['tarea_externa'] and Repo.usage(r['id_empresa'])['solicitudes'] >= int(os.getenv('MENU3D_DAILY_LIMIT','10')):
            abort(429,description='Se alcanzó el límite diario de generaciones de tu empresa.')
        result = Repo.update(resource_id,estado='en_cola',clave_idempotencia=key,
            solicitado_en=datetime.now(timezone.utc),error_codigo=None,error_mensaje=None,
            siguiente_intento=datetime.now(timezone.utc),intentos=0,lease_hasta=None,lease_token=None)
        audit('solicitar_generacion',r['id_empresa'],user['id'],resource_id)
        return result


def regenerate(resource_id):
    row,r,user = owned_resource(resource_id,'ai.business')
    with shared_transaction():
        Repo.lock_company(r['id_empresa'])
        row = Repo.resource(resource_id,lock=True)
        if row['estado'] not in ('completado','rechazado','fallido') or row['error_codigo']=='envio_incierto':
            abort(409,description='Esta versión no puede regenerarse en este momento.')
        history = Repo.history(row['id_plato'])
        if len(history)>=20 or any(h['estado'] in ('pendiente','en_cola','procesando') for h in history):
            abort(409,description='Ya existe una versión pendiente o se alcanzó el límite de versiones.')
        if Repo.usage(r['id_empresa'])['reservado'] + row['bytes_fotos'] + 52428800 > int(os.getenv('MENU3D_COMPANY_BYTES','1073741824')):
            abort(409,description='Se alcanzó la cuota de almacenamiento.')
        result = Repo.insert_resource(row['id_plato'],user['id'],row['originales'],row['fotografias'],row['bytes_fotos'])
        audit('preparar_regeneracion',r['id_empresa'],user['id'],result['id_recurso'])
        return result


def publish(pid, value):
    dish,r,user = owned_dish(pid)
    if type(value) is not bool: raise ValueError('publicado debe ser booleano.')
    with shared_transaction():
        Repo.lock_company(r['id_empresa'])
        result = Repo.publish(pid,value)
        audit('publicar' if value else 'despublicar',r['id_empresa'],user['id'],pid)
        return result


def review(resource_id, approved):
    row,r,user = owned_resource(resource_id)
    if type(approved) is not bool: raise ValueError('aprobado debe ser booleano.')
    with shared_transaction():
        Repo.lock_company(r['id_empresa'])
        row = Repo.resource(resource_id,lock=True)
        if row['estado'] != 'completado' or not row['modelo_path'] or not row['bytes_modelo']:
            abort(409,description='El modelo todavía no ha sido validado.')
        result = Repo.approve(resource_id,row['id_plato']) if approved else Repo.update(resource_id,estado='rechazado',aprobado=False)
        audit('aprobar' if approved else 'rechazar',r['id_empresa'],user['id'],resource_id)
        return result
