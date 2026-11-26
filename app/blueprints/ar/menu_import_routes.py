from flask import jsonify, request, send_file
from app.core.auth_guard import login_required
from app.services import menu3d as service
from app.services import menu_import as importer
from app.repositories.categorias_plato import CategoriasPlatoRepository
from . import bp


@bp.get('/api/gestion/restaurantes/<int:rid>/plantilla/<fmt>')
@login_required
def menu_template(rid,fmt):
    service.authorize(rid)
    return send_file(importer.template(fmt),as_attachment=True,download_name='Plantilla_platos.'+fmt,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' if fmt=='xlsx' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')


@bp.post('/api/gestion/restaurantes/<int:rid>/importar/analizar')
@login_required
def menu_import_preview(rid):
    _,user=service.authorize(rid)
    upload=request.files.get('archivo')
    if not upload or not upload.filename: raise ValueError('Selecciona una plantilla o una foto de tu carta.')
    raw=upload.read(importer.MAX_FILE+1)
    if request.form.get('tipo')=='foto':
        service.authorize(rid,'ai.business')
        dishes=importer.read_photo(raw,user['id'])
    else: dishes=importer.read_document(raw,upload.filename)
    return jsonify(success=True,platos=dishes,categorias=CategoriasPlatoRepository.list_all())


@bp.post('/api/gestion/restaurantes/<int:rid>/importar/guardar')
@login_required
def menu_import_save(rid):
    service.authorize(rid)
    body=request.get_json(silent=True)
    if not isinstance(body,dict) or body.get('confirmar') is not True:
        raise ValueError('Revisa y confirma los platos antes de registrarlos.')
    ids=importer.save_batch(rid,body.get('platos'))
    return jsonify(success=True,ids=ids,total=len(ids)),201
