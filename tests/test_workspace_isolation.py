import pytest
from app import create_app
from app.config import Config
from app.db.connection import testing_enabled as db_testing, _active_database_url, DatabaseConfigurationError

def test_flask_test_config_cannot_select_operational_database(monkeypatch):
    monkeypatch.setattr(Config,'TESTING',False)
    monkeypatch.setattr(Config,'APP_ENV','development')
    monkeypatch.setattr(Config,'DATABASE_URL','postgresql://qa:dummy@operational.invalid/main?sslmode=require')
    monkeypatch.delenv('FLASK_TESTING',raising=False)
    monkeypatch.delenv('SMARTRESTO_TEST_DATABASE_URL',raising=False)
    app=create_app({'TESTING':True,'SECRET_KEY':'test-only-'*8})
    with app.app_context():
        assert db_testing()
        with pytest.raises(DatabaseConfigurationError,match='SMARTRESTO_TEST_DATABASE_URL'):
            _active_database_url()
