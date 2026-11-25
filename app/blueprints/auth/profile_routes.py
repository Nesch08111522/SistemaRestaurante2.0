"""Personal profile routes: allowlisted fields and no caller-selected user ID."""
import re
from flask import jsonify, render_template
from app.core.auth_guard import login_required
from app.models.user import UserModel
from app.repositories.usuarios import UsuariosRestriccionesRepository
from app.blueprints.workspace import actor, body, text, WorkspaceError, workspace_errors
from . import bp


@bp.get('/profile')
@workspace_errors
@login_required
def profile():
    account = UserModel.get_by_id(actor()['id'])
    return render_template('workspace/profile.html', account=account,
                           restrictions=sorted(UsuariosRestriccionesRepository.RESTRICCIONES_VALIDAS))


@bp.patch('/api/profile')
@workspace_errors
@login_required
def update_profile():
    user = actor()
    data = body({'name','email','preferences','restrictions','current_password'})
    changes = {}
    if 'name' in data:
        changes['name'] = text(data['name'], 'el nombre', 180, required=True)
    if 'email' in data:
        email = text(data['email'], 'el correo', 254, required=True).lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            raise WorkspaceError('Ingresa un correo válido.')
        if email != (user.get('profile',{}).get('email') or '').lower():
            password = text(data.get('current_password',''), 'la contraseña actual', 256, required=True)
            if not UserModel.authenticate(user['username'], password):
                raise WorkspaceError('La contraseña actual no es correcta.', 403)
        changes['email'] = email
    for field in ('preferences','restrictions'):
        if field not in data:
            continue
        items = data[field]
        if not isinstance(items, list) or len(items) > 20:
            raise WorkspaceError('Usa una lista de hasta 20 elementos.')
        clean = list(dict.fromkeys(text(v, 'cada preferencia o restricción', 120, required=True).lower() for v in items))
        if field == 'restrictions' and set(clean) - UsuariosRestriccionesRepository.RESTRICCIONES_VALIDAS:
            raise WorkspaceError('Selecciona únicamente restricciones disponibles.')
        changes[field] = clean
    if not changes:
        raise WorkspaceError('No hay cambios para guardar.')
    if not UserModel.update_user(user['id'], changes):
        raise WorkspaceError('La cuenta ya no está disponible.', 404)
    return jsonify(success=True, message='Tu perfil se guardó correctamente.')
