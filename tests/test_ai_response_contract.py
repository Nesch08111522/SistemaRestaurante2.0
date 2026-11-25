from unittest.mock import Mock
import pytest
from app.ai import client

@pytest.mark.parametrize('content',['[]','42','null','"hello"','invalid'])
def test_invalid_ai_object_falls_back_without_optional_payload(monkeypatch,content):
    monkeypatch.setattr(client,'is_mock',lambda:False)
    monkeypatch.setattr(client,'_registrar_decision',Mock())
    monkeypatch.setattr(client,'_call_openrouter',lambda **kw:{'content':content,'modelo':'qa','elapsed_ms':0})
    result=client.call_json(kind='audit_menu',system_prompt='',user_prompt='',entidad='qa',id_usuario_actor=1)
    assert isinstance(result,dict) and 'sugerencias' in result

def test_provider_failure_without_payload_does_not_raise_type_error(monkeypatch):
    monkeypatch.setattr(client,'is_mock',lambda:False)
    monkeypatch.setattr(client,'_registrar_decision',Mock())
    monkeypatch.setattr(client,'_call_openrouter',Mock(side_effect=client._AIUnavailable()))
    assert isinstance(client.call_json(kind='recommend',system_prompt='',user_prompt='',entidad='qa',id_usuario_actor=1),dict)
