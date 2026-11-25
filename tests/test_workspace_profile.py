from unittest.mock import Mock
import pytest
from tests.test_qa_regression import app, data, sign_in
from app.models.user import UserModel

@pytest.mark.parametrize('payload', [{'role':'admin'}, {'id':2,'name':'Other'}, {'preferences':'bad'}, {'restrictions':['inventada']}, {'email':'invalid'}, {'name':'x'*181}, []])
def test_profile_rejects_bad_or_privileged_fields(app,data,monkeypatch,payload):
    update=Mock();monkeypatch.setattr(UserModel,'update_user',update)
    with app.test_client() as c:
        sign_in(c)
        assert c.patch('/auth/api/profile',json=payload).status_code==400
    update.assert_not_called()

def test_profile_writes_only_session_user_and_allowlist(app,data,monkeypatch):
    update=Mock(return_value={'id':1});monkeypatch.setattr(UserModel,'update_user',update)
    with app.test_client() as c:
        sign_in(c)
        assert c.get('/auth/profile').status_code==200
        r=c.patch('/auth/api/profile',json={'name':'Ana','preferences':['Criolla','criolla'],'restrictions':['vegano']})
        assert r.status_code==200
        assert 'password' not in r.json
    update.assert_called_once_with(1,{'name':'Ana','preferences':['criolla'],'restrictions':['vegano']})

def test_email_change_requires_current_password(app,data,monkeypatch):
    update=Mock();monkeypatch.setattr(UserModel,'update_user',update)
    with app.test_client() as c:
        sign_in(c)
        assert c.patch('/auth/api/profile',json={'email':'new@example.com','current_password':'wrong'}).status_code==403
    update.assert_not_called()

def test_private_profile_csrf_is_enforced(app,data,monkeypatch):
    app.config['WTF_CSRF_ENABLED']=True
    update=Mock();monkeypatch.setattr(UserModel,'update_user',update)
    with app.test_client() as c:
        sign_in(c)
        assert c.patch('/auth/api/profile',json={'name':'Ana'}).status_code==400
    update.assert_not_called()
