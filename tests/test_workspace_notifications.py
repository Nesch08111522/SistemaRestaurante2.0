from unittest.mock import Mock
from tests.test_qa_regression import app, data, sign_in
from app.models.notification import NotificationModel
from app.repositories.notificaciones import NotificacionesRepository

def test_cannot_mark_other_users_notification(app,data,monkeypatch):
    monkeypatch.setattr(NotificacionesRepository,'get_by_id',lambda *a:{'id_usuario':2})
    mark=Mock();monkeypatch.setattr(NotificationModel,'mark_read',mark)
    with app.test_client() as c:
        sign_in(c)
        assert c.post('/auth/api/notifications/5/read',json={}).status_code==404
    mark.assert_not_called()

def test_mark_all_uses_only_actor(app,data,monkeypatch):
    mark=Mock(return_value=3);monkeypatch.setattr(NotificationModel,'mark_all_read',mark)
    with app.test_client() as c:
        sign_in(c)
        assert c.post('/auth/api/notifications/read-all',json={'id_usuario':2}).status_code==400
        assert c.post('/auth/api/notifications/read-all',json={}).json['count']==3
    mark.assert_called_once_with(1)

def test_inbox_does_not_render_unsafe_links(app,data,monkeypatch):
    monkeypatch.setattr(NotificationModel,'list_by_usuario',lambda *a,**k:[dict(id_notificacion=1,titulo='Aviso',mensaje='<img onerror=alert(1)>',enlace='javascript:alert(1)',leida=False)])
    with app.test_client() as c:
        sign_in(c);r=c.get('/auth/notifications')
        assert r.status_code==200
        assert 'javascript:' not in r.text
        assert '<img onerror' not in r.text
