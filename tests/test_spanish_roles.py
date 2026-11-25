"""Role aliases and real rendered navigation; all account reads are mocked."""
import pytest
from flask import url_for
from app.core.permissions import can
from tests.test_qa_regression import app, data, sign_in

@pytest.mark.parametrize("stored,canonical,destination", [
    ("usuario", "diner", "auth.workspace_home"),
    ("empresario", "business_owner", "owner.dashboard"),
    ("admin", "admin", "admin.dashboard"),
])
def test_login_profile_and_menu_for_spanish_roles(app, data, stored, canonical, destination):
    row, _ = data
    row["rol"] = stored
    with app.test_client() as client:
        response = client.post("/auth/login", data={"username":"qa", "password":"QA-only-pass123"})
        assert response.status_code == 302
        assert client.get("/auth/api/whoami").json["user"]["role"] == canonical
        home = client.get("/")
        assert home.status_code == 200
        assert '<a href="/auth/profile">Mi perfil</a>' in home.text
        assert 'data-pendiente="auth.profile"' not in home.text
        with app.test_request_context():
            assert f'href="{url_for(destination)}">Ir al sistema' in home.text
        assert client.get("/auth/profile").status_code == 200
        assert client.get("/owner/api/resumen").status_code == (403 if stored == "usuario" else 200)
        if stored != "admin":
            assert client.get("/admin/").status_code == 403
    assert row["rol"] == stored

def test_alias_permissions_do_not_escalate_users():
    assert can("usuario", "profile.update")
    assert not can("usuario", "business.manage")
    assert not can("empresario", "platform.users.manage")
    assert can("empresario", "business.manage")
    assert can("admin", "platform.users.manage")
    assert not can("unknown", "profile.update")

def test_existing_session_revalidates_changed_role(app, data):
    row, _ = data
    with app.test_client() as client:
        sign_in(client)
        row["rol"] = "empresario"
        assert client.get("/auth/api/whoami").json["user"]["role"] == "business_owner"
        row["rol"] = "usuario"
        assert client.get("/owner/api/resumen").status_code == 403
