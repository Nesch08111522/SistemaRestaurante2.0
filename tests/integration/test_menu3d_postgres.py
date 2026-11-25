"""Real PostgreSQL queue/constraint tests, opt-in on an independent test database.
No operational tables are modified: a random schema is created inside a transaction
and rolled back. No provider/Storage calls. Not a substitute for Supabase RLS tests.
"""
import os
import re
import uuid
from pathlib import Path
from contextlib import contextmanager
import pytest
import psycopg
from psycopg.rows import dict_row
from app.db.connection import _active_database_url
from app.repositories.menu3d import Menu3DRepository as Repo


@pytest.fixture
def database(monkeypatch):
    if not os.getenv('SMARTRESTO_TEST_DATABASE_URL'):
        pytest.skip('Independent SMARTRESTO_TEST_DATABASE_URL is not configured')
    monkeypatch.setenv('FLASK_TESTING','1')
    # Existing guard rejects a test database matching the operational database.
    dsn=_active_database_url()
    schema='smartresto_qa_'+uuid.uuid4().hex
    with psycopg.connect(dsn,row_factory=dict_row,connect_timeout=5,sslmode='require') as conn:
        try:
            conn.execute(f'CREATE SCHEMA {schema}')
            conn.execute(f'CREATE TABLE {schema}.empresas(id_empresa bigint PRIMARY KEY)')
            conn.execute(f'CREATE TABLE {schema}.usuarios(id_usuario bigint PRIMARY KEY)')
            conn.execute(f'CREATE TABLE {schema}.restaurantes(id_restaurante bigint PRIMARY KEY,id_empresa bigint)')
            conn.execute(f'CREATE TABLE {schema}.platos(id_plato bigint PRIMARY KEY,id_restaurante bigint)')
            migration=Path('migrations/20261124_menu3d.sql').read_text(encoding='utf-8')
            statements=re.findall(r'CREATE (?:TABLE|UNIQUE INDEX|INDEX)\s+[^;]+;',migration,re.S)
            for statement in statements:conn.execute(statement.replace('public.',schema+'.'))
            conn.execute(f'INSERT INTO {schema}.empresas VALUES(1)')
            conn.execute(f'INSERT INTO {schema}.usuarios VALUES(1)')
            conn.execute(f'INSERT INTO {schema}.restaurantes VALUES(1,1)')
            conn.execute(f'INSERT INTO {schema}.platos VALUES(1,1)')
            def query(sql,args=(),many=False):
                cur=conn.execute(sql.replace('public.',schema+'.'),args)
                return list(cur.fetchall()) if many else cur.fetchone()
            monkeypatch.setattr('app.repositories.menu3d.query',query)
            yield conn,schema
        finally:
            conn.rollback() # Includes the schema and all test data.


def test_queue_claim_lease_prevents_second_worker(database):
    row=Repo.insert_resource(1,1,['a'],['b'],10)
    Repo.update(row['id_recurso'],estado='en_cola')
    first=Repo.claim(uuid.uuid4());assert first['id_recurso']==row['id_recurso']
    assert Repo.claim(uuid.uuid4()) is None


def test_unique_active_job_and_approval_constraints(database):
    conn,schema=database
    first=Repo.insert_resource(1,1,['a'],['b'],10);second=Repo.insert_resource(1,1,['c'],['d'],10)
    assert second['version']==first['version']+1
    Repo.update(first['id_recurso'],estado='en_cola')
    with pytest.raises(psycopg.errors.UniqueViolation):
        with conn.transaction():Repo.update(second['id_recurso'],estado='en_cola')
    with pytest.raises(psycopg.errors.CheckViolation):
        with conn.transaction():Repo.update(second['id_recurso'],aprobado=True)


def test_expired_lease_is_recoverable(database):
    conn,schema=database
    row=Repo.insert_resource(1,1,['a'],['b'],10);Repo.update(row['id_recurso'],estado='en_cola')
    Repo.claim(uuid.uuid4())
    conn.execute(f"UPDATE {schema}.platos_recursos3d SET lease_hasta=now()-interval '1 second'")
    token=uuid.uuid4();assert Repo.claim(token)['lease_token']==token
