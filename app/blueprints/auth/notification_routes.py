"""Authenticated inbox backed by the existing relational notification model."""
from flask import jsonify, render_template
from app.core.auth_guard import login_required
from app.core.security import is_safe_redirect_url
from app.models.notification import NotificationModel
from app.repositories.notificaciones import NotificacionesRepository
from app.blueprints.workspace import actor, body, WorkspaceError, workspace_errors
from . import bp


@bp.get('/notifications')
@workspace_errors
@login_required
def notifications():
    rows = NotificationModel.list_by_usuario(actor()['id'], limit=100)
    rows = [{**n, 'safe_link': n.get('enlace') if is_safe_redirect_url(n.get('enlace')) else None} for n in rows]
    return render_template('workspace/notifications.html', notifications=rows)


@bp.post('/api/notifications/<int:notification_id>/read')
@workspace_errors
@login_required
def read_notification(notification_id):
    body(set())
    notification = NotificacionesRepository.get_by_id(notification_id)
    if not notification or notification.get('id_usuario') != actor()['id']:
        raise WorkspaceError('Notificación no encontrada.', 404)
    NotificationModel.mark_read(notification_id)
    return jsonify(success=True, message='Notificación marcada como leída.')


@bp.post('/api/notifications/read-all')
@workspace_errors
@login_required
def read_all_notifications():
    body(set())
    count = NotificationModel.mark_all_read(actor()['id'])
    return jsonify(success=True, count=count, message='Notificaciones marcadas como leídas.')
