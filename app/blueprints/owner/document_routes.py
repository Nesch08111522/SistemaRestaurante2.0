"""Read-only document suggestions. Applying and saving are separate user actions."""
from flask import jsonify, request, send_file
from app.core.auth_guard import login_required, role_required
from app.blueprints.workspace import actor, workspace_errors, WorkspaceError
from app.repositories.categorias import CategoriasRepository
from app.services.business_document import extract_document, MAX_UPLOAD
from app.ai.business_document import analyze_document
from app.services.business_templates import excel_template, word_template
from . import bp


@bp.post('/api/documento/analizar')
@workspace_errors
@login_required
@role_required('business_owner','business_admin','manager')
def analyze_business_upload():
    upload=request.files.get('file')
    if not upload or not upload.filename:
        raise WorkspaceError('Selecciona un archivo Excel .xlsx o Word .docx.')
    content=upload.read(MAX_UPLOAD+1)
    text,warnings=extract_document(content,upload.filename)
    proposals,ai_warnings=analyze_document(text,CategoriasRepository.list_all(),actor()['id'])
    return jsonify(success=True,proposals=proposals,warnings=warnings+ai_warnings)


@bp.get('/documento/plantilla/<string:format_name>')
@workspace_errors
@login_required
@role_required('business_owner','business_admin','manager')
def download_business_template(format_name):
    categories = CategoriasRepository.list_all()
    if format_name == 'xlsx':
        return send_file(excel_template(categories), as_attachment=True,
            download_name='Plantilla_datos_negocio_SmartResto.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    if format_name == 'docx':
        return send_file(word_template(categories), as_attachment=True,
            download_name='Plantilla_datos_negocio_SmartResto.docx',
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    raise WorkspaceError('Formato de plantilla no disponible.', 404)
