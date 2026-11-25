"""Durable worker, run separately from Flask HTTP processes."""
import logging
import time
import uuid
from datetime import datetime, timedelta, timezone
import click
from app.ai.image_to_3d import provider
from app.repositories.menu3d import Menu3DRepository as Repo
from app.services.menu3d_storage import Storage, IntegrationError
from app.services.menu3d_validation import validate_glb

logger = logging.getLogger(__name__)


def process_one():
    token = uuid.uuid4()
    row = Repo.claim(token)
    if not row: return False
    rid = row['id_recurso']
    def update(**fields):
        return Repo.job_update(rid,token,**fields)
    def finish(**fields):
        return update(lease_token=None,lease_hasta=None,**fields)
    now = datetime.now(timezone.utc)
    try:
        if row['envio_iniciado'] and not row['tarea_externa']:
            finish(estado='fallido',error_codigo='envio_incierto',
                   error_mensaje='Recupera el identificador de la tarea en Meshy. No se reenviará para evitar cargos duplicados.')
            return True
        api, storage = provider(), Storage()
        if not row['tarea_externa']:
            urls = [storage.sign(path,3600) for path in row['fotografias']]
            update(envio_iniciado=True,estado='procesando')
            row['envio_iniciado'] = True
            task_id = api.submit(urls)
            update(tarea_externa=task_id)
            row['tarea_externa'] = task_id
        task = api.status(row['tarea_externa'],len(row['fotografias']))
        state = task['status']
        if state in ('FAILED','CANCELED'):
            finish(estado='fallido',error_codigo='proveedor_fallido',finalizado_en=now,
                   error_mensaje='El proveedor no pudo generar el modelo. Revisa las fotografías y crea una nueva versión.')
        elif state == 'SUCCEEDED':
            url = (task.get('model_urls') or {}).get('glb')
            if not isinstance(url,str): raise ValueError('El proveedor no entregó un GLB.')
            data,mime = api.download(url)
            validate_glb(data,mime)
            path = row['fotografias'][0].split('/procesadas/')[0] + f'/modelos-3d/{rid}.glb'
            storage.upload(path,data,'model/gltf-binary')
            finish(estado='completado',progreso=100,modelo_path=path,bytes_modelo=len(data),
                   finalizado_en=now,error_codigo=None,error_mensaje=None)
        else:
            if row['solicitado_en'] and now-row['solicitado_en'] > timedelta(hours=24):
                finish(estado='fallido',error_codigo='tiempo_agotado',error_mensaje='La tarea excedió 24 horas. Puedes reanudar la consulta sin generar otra tarea.')
            else:
                finish(estado='procesando',progreso=max(0,min(99,int(task.get('progress') or 0))),
                       siguiente_intento=now+timedelta(seconds=20),intentos=0)
    except ValueError as exc:
        finish(estado='rechazado',error_codigo='resultado_invalido',error_mensaje=str(exc),finalizado_en=now)
    except IntegrationError as exc:
        attempts = row['intentos']+1
        ambiguous = row['envio_iniciado'] and not row['tarea_externa']
        finish(estado='fallido' if ambiguous or attempts>=6 else 'procesando',intentos=attempts,
               error_codigo='envio_incierto' if ambiguous else 'servicio_temporal',error_mensaje=str(exc),
               siguiente_intento=now+timedelta(seconds=min(900,20*2**attempts)))
    logger.info('menu3d worker processed resource=%s',rid)
    return True


def register_cli(app):
    @app.cli.command('menu3d-worker')
    @click.option('--once',is_flag=True,help='Procesa como máximo una tarea y termina.')
    def worker(once):
        """Process PostgreSQL jobs under a service supervisor."""
        provider(); Storage()
        while True:
            try: worked = process_one()
            except Exception:
                logger.error('menu3d worker interrupted; lease recovery will resume persisted jobs')
                if once: raise click.ClickException('Trabajador interrumpido; revisa BD y configuración.') from None
                worked = False
            if once: break
            if not worked: time.sleep(5)

    @app.cli.command('menu3d-recover')
    @click.argument('resource_id',type=int)
    @click.argument('external_id')
    def recover(resource_id,external_id):
        """Attach an EXISTING Meshy task after an uncertain submission; no paid POST."""
        from app.db.repository import shared_transaction
        from app.repositories.auditoria import EventosAuditoriaRepository
        with shared_transaction():
            row = Repo.resource(resource_id,lock=True)
            if not row or row['error_codigo'] != 'envio_incierto' or row['tarea_externa']:
                raise click.ClickException('El recurso no tiene un envío incierto recuperable.')
            provider().status(external_id,len(row['fotografias']))
            Repo.update(resource_id,tarea_externa=external_id,estado='en_cola',
                siguiente_intento=datetime.now(timezone.utc),error_codigo=None,error_mensaje=None)
            EventosAuditoriaRepository.record(accion='menu3d.recuperar_tarea',tipo_recurso='menu3d',
                id_empresa=row['id_empresa'],id_recurso=str(resource_id))
        click.echo('Tarea existente vinculada. El trabajador retomará la consulta.')
