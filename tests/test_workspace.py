"""Private-system tests. Existing fixture forbids all real database connections."""
import re
from pathlib import Path
import pytest
from tests.test_qa_regression import app, data, sign_in


def test_workspace_requires_login(app):
    response = app.test_client().get('/auth/inicio')
    assert response.status_code == 302
    assert '/auth/login' in response.location


@pytest.mark.parametrize('role', ['diner','business_owner','manager','waiter','kitchen','admin'])
def test_workspace_has_role_navigation_and_no_public_assets(app,data,role):
    data[0]['rol'] = role
    with app.test_client() as client:
        sign_in(client)
        response = client.get('/auth/inicio')
        assert response.status_code == 200
        assert 'css/workspace.css' in response.text
        assert 'css/site.css' not in response.text
        assert ('href="/admin/"' in response.text) == (role == 'admin')
        assert ('href="/salon/"' in response.text) == (role in {'business_owner','manager','waiter','admin'})
        for asset in re.findall(r'(?:href|src)="(/static/[^"?]+)', response.text):
            assert client.get(asset).status_code == 200, asset


def test_logout_get_does_not_change_session(app,data):
    with app.test_client() as client:
        sign_in(client)
        assert client.get('/auth/logout').status_code == 200
        with client.session_transaction() as session:
            assert session['user_id'] == 1
        assert client.post('/auth/logout').status_code == 302
        with client.session_transaction() as session:
            assert 'user_id' not in session


def test_login_enters_private_workspace(app,data):
    response=app.test_client().post('/auth/login',data={'username':'qa','password':'QA-only-pass123'})
    assert response.location.endswith('/auth/inicio')
