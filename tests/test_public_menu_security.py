from tests.test_qa_regression import app, data


def test_unpublished_restaurant_menu_is_not_public(app, data, monkeypatch):
    monkeypatch.setattr('app.models.restaurant.RestaurantModel.get_by_id',
                        lambda *a, **k: {'id_restaurante': 1, 'estado_publicacion': 'unpublished'})
    client = app.test_client()
    assert client.get('/negocio/1').status_code == 404
    assert client.get('/negocio/1/api/menu').status_code == 404


def test_public_menu_uses_only_published_projection(app, data, monkeypatch):
    monkeypatch.setattr('app.repositories.platos.PlatosRepository.list_publicados',
                        lambda rid: [{'id_plato': 8, 'nombre': 'Plato público', 'precio': 10}])
    client = app.test_client()
    assert [dish['nombre'] for dish in client.get('/negocio/1/api/menu').json['platos']] == ['Plato público']
