from contextlib import nullcontext
from unittest.mock import Mock

from tests.test_qa_regression import app, data, sign_in


def test_only_admin_can_approve_and_audit(app, data, monkeypatch):
    approve = Mock(return_value={'id_restaurante': 296, 'id_empresa': 10})
    audit = Mock()
    monkeypatch.setattr('app.repositories.restaurantes.RestaurantesRepository.approve_and_publish', approve)
    monkeypatch.setattr('app.repositories.auditoria.EventosAuditoriaRepository.record', audit)
    monkeypatch.setattr('app.blueprints.admin.shared_transaction', nullcontext)
    client = app.test_client()
    sign_in(client)
    assert client.post('/admin/moderaciones/296/aprobar').status_code == 403
    approve.assert_not_called()
    data[0]['rol'] = 'admin'
    assert client.post('/admin/moderaciones/296/aprobar').status_code == 302
    approve.assert_called_once_with(296)
    assert audit.call_args.kwargs['id_usuario_actor'] == 1


def test_stock_rejects_foreign_restaurant_and_validates_body(app, data, monkeypatch):
    from app.services import menu3d
    from werkzeug.exceptions import Forbidden
    update = Mock()
    monkeypatch.setattr('app.services.commerce.adjust_stock', update)
    monkeypatch.setattr(menu3d, 'owned_dish', Mock(side_effect=Forbidden()))
    client = app.test_client()
    sign_in(client)
    assert client.put('/ar/api/gestion/platos/249/stock', json={'cantidad': 5, 'version': 0}).status_code == 403
    update.assert_not_called()
