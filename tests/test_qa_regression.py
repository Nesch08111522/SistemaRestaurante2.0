"""Offline QA: no real accounts, network calls or production writes."""
import re
from pathlib import Path
from unittest.mock import Mock
import pytest
from werkzeug.security import generate_password_hash
from app import create_app
from app.db.connection import DatabaseConnectionError
from app.models.user import UserModel

ROLES = ["diner", "business_owner", "business_admin", "manager", "cashier", "waiter", "kitchen", "admin"]
PASSWORD = generate_password_hash("QA-only-pass123")

@pytest.fixture
def app(monkeypatch):
    # Fail immediately if a test unexpectedly reaches any real DB connection.
    monkeypatch.setattr("app.db.connection.psycopg.connect", Mock(side_effect=AssertionError("Real DB forbidden")))
    return create_app({"TESTING": True, "SECRET_KEY": "qa" * 32, "WTF_CSRF_ENABLED": False})

@pytest.fixture
def data(monkeypatch):
    row = dict(id_usuario=1, nombre_usuario="qa", hash_contrasena=PASSWORD, rol="diner", estado_cuenta="ACTIVE")
    user_read = Mock(side_effect=lambda *a: dict(row))
    monkeypatch.setattr("app.repositories.usuarios.UsuariosRepository.get_by_id", user_read)
    monkeypatch.setattr("app.repositories.usuarios.UsuariosRepository.get_by_login", lambda *a: dict(row))
    for name in ["UsuariosPreferenciasRepository", "UsuariosRestriccionesRepository"]:
        monkeypatch.setattr("app.repositories.usuarios." + name + ".list_for_user", lambda *a: [])
    monkeypatch.setattr("app.repositories.usuarios.UsuariosDetallesNegocioRepository.get_for_user", lambda *a: None)
    restaurant = dict(id_restaurante=1, id_empresa=1, nombre="QA restaurante", descripcion="Cocina", estado_publicacion="published", platos=[])
    company = dict(id_empresa=1, nombre="QA empresa", estado="active", suscripcion={"plan": "basic"})
    monkeypatch.setattr("app.models.company.get_company_for_user", lambda *a: company)
    monkeypatch.setattr("app.repositories.categorias.CategoriasRepository.list_all", lambda: [])
    monkeypatch.setattr("app.repositories.restaurantes.RestaurantesRepository.list_published", lambda **k: [restaurant])
    monkeypatch.setattr("app.models.restaurant.RestaurantModel.list_published", lambda **k: [restaurant])
    monkeypatch.setattr("app.models.restaurant.RestaurantModel.list_by_empresa", lambda *a: [restaurant])
    monkeypatch.setattr("app.models.restaurant.RestaurantModel.get_by_id", lambda *a, **k: restaurant)
    monkeypatch.setattr("app.repositories.platos.PlatosRepository.list_publicados", lambda *a: [])
    monkeypatch.setattr("app.models.menu.MenuModel.list_by_restaurante", lambda *a, **k: [])
    monkeypatch.setattr("app.models.review.ReviewModel.list_by_restaurante", lambda *a, **k: [])
    monkeypatch.setattr("app.models.review.ReviewModel.summary", lambda *a: dict(total_resenas=0, promedio_calificacion=0))
    monkeypatch.setattr("app.models.promotion.PromotionModel.list_by_restaurante", lambda *a, **k: [])
    monkeypatch.setattr("app.repositories.empresas.EmpresasRepository.list_all", lambda **k: [company])
    monkeypatch.setattr("app.repositories.usuarios.UsuariosRepository.list_by_role", lambda *a, **k: [row])
    monkeypatch.setattr('app.models.order.OrderModel.list_by_restaurante', lambda *a, **k: [])
    return row, user_read

def sign_in(client):
    with client.session_transaction() as s:
        s["user_id"] = 1
        s["user"] = {"id": 1, "role": "diner"}

@pytest.mark.parametrize("path", ["/", "/auth/login", "/auth/register", "/auth/recover", "/descubrir/", "/negocio/1", "/mercado/", "/ar/"])
def test_public_views(app, data, path):
    with app.test_client() as c:
        response = c.get(path)
        assert response.status_code == 200
        assert "/mi-cocina" not in response.text
        assert b"food-scene.js" not in response.data
        assert b"chart-4.3.0" not in response.data
        for asset in re.findall(r'(?:src|href)="(/static/[^"?]+)', response.text):
            assert c.get(asset).status_code == 200, asset

@pytest.mark.parametrize("role", ROLES)
def test_login_and_all_private_views(app, data, role):
    row, reads = data
    row["rol"] = role
    allowed = {"/admin/": {"admin"}, "/owner/": {"business_owner", "business_admin", "manager", "admin"},
               "/salon/": {"business_owner", "business_admin", "manager", "cashier", "waiter", "admin"},
               "/kitchen/": {"business_owner", "business_admin", "manager", "kitchen", "admin"}}
    with app.test_client() as c:
        assert c.post("/auth/login", data={"username": "qa", "password": "QA-only-pass123"}).status_code == 302
        for path in ["/", "/admin/", "/owner/", "/salon/", "/kitchen/", "/recompensas/"]:
            reads.reset_mock()
            response = c.get(path)
            assert response.status_code == (403 if path in allowed and role not in allowed[path] else 200), (role, path)
            assert reads.call_count == 1
        assert c.get("/auth/api/whoami").json["authenticated"] is True
        assert c.post("/auth/logout").status_code == 302
        assert c.get("/auth/api/whoami").json["authenticated"] is False

@pytest.mark.parametrize("path", ["/api/user/1", "/api/user/1/orders", "/api/user/1/notifications", "/api/user/1/favorites", "/api/user/1/search-history", "/api/user/1/companies", "/api/company/1", "/api/audit/1", "/api/order/1", "/api/restaurant/1/orders", "/api/groups/1", "/api/ai-decisions/1", "/api/moderations/1"])
def test_private_apis_require_login(app, path):
    assert app.test_client().get(path).status_code == 401

@pytest.mark.parametrize("path", ["/api/user/2", "/api/user/2/orders", "/api/audit/1", "/api/moderations/1"])
def test_private_api_scope(app, data, path):
    with app.test_client() as c:
        sign_in(c)
        assert c.get(path).status_code == 403

@pytest.mark.parametrize("status", ["INACTIVE", "BLOCKED", None])
def test_inactive_account(app, data, status):
    data[0]["estado_cuenta"] = status
    with app.test_client() as c:
        assert c.post("/auth/login", data={"username": "qa", "password": "QA-only-pass123"}).status_code == 401
        sign_in(c)
        assert c.get("/auth/api/whoami").json["authenticated"] is False


def test_login_does_not_query_categories(app, monkeypatch):
    monkeypatch.setattr("app.repositories.categorias.CategoriasRepository.list_all", Mock(side_effect=AssertionError("Unnecessary SQL")))
    assert app.test_client().get("/auth/login").status_code == 200


def test_outage_returns_503_without_recursive_sql(app, monkeypatch):
    monkeypatch.setattr("app.models.user.UserModel.get_session_account", Mock(side_effect=DatabaseConnectionError("offline")))
    with app.test_client() as c:
        sign_in(c)
        for path in ["/admin/", "/auth/api/whoami"]:
            response = c.get(path)
            assert response.status_code == 503
            assert response.headers["Retry-After"] == "30"


def test_liveness_readiness(app, monkeypatch):
    c = app.test_client()
    assert c.get("/health").status_code == 200
    monkeypatch.setattr("app.db.connection.check_connection", lambda: True)
    assert c.get("/ready").status_code == 200
    monkeypatch.setattr("app.db.connection.check_connection", Mock(side_effect=DatabaseConnectionError("offline")))
    assert c.get("/ready").status_code == 503


def test_csrf_and_external_redirect(app, data):
    app.config["WTF_CSRF_ENABLED"] = True
    assert app.test_client().post("/auth/login", data={"username": "qa", "password": "QA-only-pass123"}).status_code == 400
    app.config["WTF_CSRF_ENABLED"] = False
    response = app.test_client().post("/auth/login", data={"username": "qa", "password": "QA-only-pass123", "next": "https://example.com"})
    assert response.headers["Location"] == "/auth/inicio"


def test_search_contract(app, data):
    response = app.test_client().get("/descubrir/api/restaurants?q=QA")
    assert response.status_code == 200
    assert response.json["restaurantes"][0]["nombre"] == "QA restaurante"


@pytest.mark.parametrize("authenticated", [False, True])
@pytest.mark.parametrize("path", ["/mi-cocina/", "/mi-cocina/api/despensa"])
def test_home_kitchen_removed(app, data, authenticated, path):
    with app.test_client() as client:
        if authenticated:
            sign_in(client)
        assert client.get(path).status_code == 404
