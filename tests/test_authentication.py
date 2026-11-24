"""Authentication regression tests; no live credentials or database writes."""
from contextlib import contextmanager
from unittest.mock import MagicMock
import pytest
from werkzeug.security import generate_password_hash
from app.models.user import UserModel
from app.repositories.usuarios import UsuariosRepository
from tests.test_qa_regression import app, data

@pytest.mark.parametrize("identifier", ["qa", "persona@example.com", "PERSONA@EXAMPLE.COM"])
def test_valid_credentials_by_username_or_email(monkeypatch, identifier):
    row = dict(id_usuario=1, nombre_usuario="qa", correo="persona@example.com", rol="diner", estado_cuenta="ACTIVE", hash_contrasena=generate_password_hash("valid-pass"))
    captured = []
    cursor = MagicMock()
    cursor.__enter__.return_value = cursor
    cursor.fetchall.return_value = [row]
    cursor.execute.side_effect = lambda sql, params: captured.append((sql, params))
    conn = MagicMock()
    conn.cursor.return_value = cursor
    @contextmanager
    def transaction(): yield conn
    monkeypatch.setattr("app.repositories.usuarios.shared_transaction", transaction)
    assert UserModel.authenticate(identifier, "valid-pass")["id"] == 1
    assert "lower(correo)=lower(%s)" in captured[0][0]
    assert captured[0][1] == (identifier, identifier, identifier)
    assert UserModel.authenticate(identifier, "wrong-pass") is None

@pytest.mark.parametrize("rows,identifier,expected", [
    ([], "missing", None),
    ([{"nombre_usuario":"a"},{"nombre_usuario":"b"}], "shared@example.com", None),
    ([{"nombre_usuario":"exact"},{"nombre_usuario":"b"}], "exact", "exact"),
])
def test_lookup_does_not_choose_ambiguous_email(monkeypatch, rows, identifier, expected):
    cursor = MagicMock()
    cursor.__enter__.return_value = cursor
    cursor.fetchall.return_value = rows
    conn = MagicMock()
    conn.cursor.return_value = cursor
    @contextmanager
    def transaction(): yield conn
    monkeypatch.setattr("app.repositories.usuarios.shared_transaction", transaction)
    result = UsuariosRepository.get_by_login(identifier)
    assert (result["nombre_usuario"] if result else None) == expected

@pytest.mark.parametrize("stored", [None, "", "plain-password", "unknown$invalid$value"])
def test_invalid_hash_does_not_crash_or_authenticate(monkeypatch, stored):
    monkeypatch.setattr(UsuariosRepository, "get_by_login", lambda *a: dict(id_usuario=1,nombre_usuario="qa",rol="diner",estado_cuenta="ACTIVE",hash_contrasena=stored))
    assert UserModel.authenticate("qa", "plain-password") is None


def test_form_preserves_password_and_trims_identifier(app, data, monkeypatch):
    captured = []
    monkeypatch.setattr(UserModel, "authenticate", lambda identifier, password: captured.append((identifier,password)))
    response = app.test_client().post("/auth/login", data={"username":"  person@example.com  ","password":" pass with spaces "})
    assert response.status_code == 401
    assert captured == [("person@example.com", " pass with spaces ")]


def test_database_failure_is_not_invalid_credentials(app, monkeypatch):
    from app.db.connection import DatabaseConnectionError
    def unavailable(*args): raise DatabaseConnectionError("offline")
    monkeypatch.setattr(UsuariosRepository, "get_by_login", unavailable)
    response = app.test_client().post("/auth/login", data={"username":"qa","password":"valid-pass"})
    assert response.status_code == 503


def test_rejection_diagnostics_do_not_log_credentials(monkeypatch, caplog):
    row = dict(id_usuario=1,nombre_usuario="private-admin",rol="admin",estado_cuenta="ACTIVE",hash_contrasena="$2b$private-hash")
    monkeypatch.setattr(UsuariosRepository, "get_by_login", lambda *a: row)
    assert UserModel.authenticate("private-admin", "private-password") is None
    assert "reason=password_format_unsupported format=bcrypt" in caplog.text
    assert "private-" not in caplog.text


def test_login_error_displayed_once(app, monkeypatch):
    monkeypatch.setattr(UserModel, "authenticate", lambda *a: None)
    response = app.test_client().post("/auth/login", data={"username":"admin", "password":"invalid"})
    assert response.status_code == 401
    assert response.text.count("Usuario o contraseña incorrectos.") == 1


@pytest.mark.parametrize("state,pending,allowed", [
    (None, False, True), (None, True, False), (None, None, False),
    ("ACTIVE", False, True), ("ACTIVE", True, False),
    ("INACTIVE", False, False), ("BLOCKED", False, False),
    ("", False, False), ("UNKNOWN", False, False),
])
def test_account_state_policy(state, pending, allowed):
    assert UserModel.is_active({"estado_cuenta": state, "activacion_pendiente": pending}) is allowed
    assert UserModel.is_active({"status": state, "activacion_pendiente": pending}) is allowed


def test_legacy_admin_login_session_and_authorization(app, data):
    row, reads = data
    row.update(rol="admin", estado_cuenta=None, activacion_pendiente=False)
    with app.test_client() as client:
        assert client.post("/auth/login", data={"username":"qa", "password":"wrong"}).status_code == 401
        assert client.post("/auth/login", data={"username":"qa", "password":"QA-only-pass123"}).status_code == 302
        assert client.get("/auth/api/whoami").json["user"]["role"] == "admin"
        assert client.get("/admin/").status_code == 200
        row["estado_cuenta"] = "INACTIVE"
        assert client.get("/auth/api/whoami").json["authenticated"] is False


def test_pending_legacy_account_cannot_login(app, data):
    data[0].update(estado_cuenta=None, activacion_pendiente=True)
    assert app.test_client().post("/auth/login", data={"username":"qa", "password":"QA-only-pass123"}).status_code == 401
