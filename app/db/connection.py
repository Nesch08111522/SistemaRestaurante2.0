# app/db/connection.py
"""
Conexión PostgreSQL de SmartResto con Supabase.

- PostgreSQL como único motor de persistencia.
- Conexión mediante psycopg 3.
- SSL obligatorio.
- Pool de conexiones limitado.
- Control de tiempos de consulta y bloqueo.
- Aislamiento de pruebas mediante una base de datos independiente.
- Sin fallback a archivos JSON.
- Sin creación ni modificación automática del esquema.
"""

from __future__ import annotations

import logging
import os
import re

from contextlib import contextmanager
from time import perf_counter
from typing import Iterator
from urllib.parse import parse_qs, parse_qsl, urlencode, urlsplit, urlunsplit

from app.config import Config
from app.db.pool import get_pool, PoolBusy, PoolCoolingDown
from app.db.metrics import TimedCursor, observe

logger = logging.getLogger(__name__)


try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    psycopg = None
    dict_row = None


class DatabaseConfigurationError(RuntimeError):
    """La configuración PostgreSQL está incompleta o es inválida."""


class DatabaseConnectionError(RuntimeError):
    """La base de datos no está disponible."""


_TEST_SCHEMA_PATTERN = re.compile(r"smartresto_qa_[a-f0-9]{32}")
_IDENTIFIER_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def testing_enabled() -> bool:
    return bool(
        getattr(Config, "TESTING", False)
        or str(getattr(Config, "APP_ENV", "")).lower() == "test"
        or os.environ.get("FLASK_TESTING", "").strip().lower()
        in {"1", "true", "yes", "on"}
    )


def test_schema() -> str:
    schema = os.environ.get("SMARTRESTO_TEST_SCHEMA", "").strip()
    if schema and not _TEST_SCHEMA_PATTERN.fullmatch(schema):
        raise DatabaseConfigurationError(
            "SMARTRESTO_TEST_SCHEMA no tiene un nombre autorizado."
        )
    return schema


def _active_database_url() -> str:
    if testing_enabled():
        test_url = os.environ.get("SMARTRESTO_TEST_DATABASE_URL", "").strip()
        if not test_url:
            raise DatabaseConfigurationError(
                "Las pruebas requieren SMARTRESTO_TEST_DATABASE_URL. "
                "No se permite utilizar DATABASE_URL como sustituto."
            )
        production_url = str(getattr(Config, "DATABASE_URL", "") or "").strip()
        if production_url:
            try:
                production = urlsplit(production_url)
                testing = urlsplit(test_url)
                same_target = (
                    production.hostname == testing.hostname
                    and production.port == testing.port
                    and production.path == testing.path
                )
                if same_target:
                    raise DatabaseConfigurationError(
                        "La base de datos de pruebas coincide con la operativa."
                    )
            except ValueError:
                raise DatabaseConfigurationError(
                    "No se pudieron comparar las conexiones de prueba."
                ) from None
        return test_url
    database_url = str(getattr(Config, "DATABASE_URL", "") or "").strip()
    if not database_url:
        raise DatabaseConfigurationError("DATABASE_URL no está configurada.")
    return database_url


def _parse_database_url(dsn: str):
    if not dsn:
        raise DatabaseConfigurationError("La URI de PostgreSQL está vacía.")
    try:
        parts = urlsplit(dsn)
        if parts.scheme.lower() not in {"postgres", "postgresql"}:
            raise DatabaseConfigurationError(
                "DATABASE_URL debe utilizar postgres:// o postgresql://."
            )
        host = parts.hostname
        port = parts.port
    except ValueError:
        raise DatabaseConfigurationError(
            "DATABASE_URL contiene un host o puerto inválido."
        ) from None
    if not host:
        raise DatabaseConfigurationError("DATABASE_URL no contiene un host válido.")
    if not parts.path or parts.path.strip("/") == "":
        raise DatabaseConfigurationError(
            "DATABASE_URL debe especificar el nombre de la base de datos."
        )
    if port is not None and not 1 <= port <= 65535:
        raise DatabaseConfigurationError(
            "El puerto PostgreSQL debe estar entre 1 y 65535."
        )
    if host.lower() in {"host_pooler", "pooler-host", "host", "region"} or any(
        c in host for c in "[]<>_"
    ):
        raise DatabaseConfigurationError(
            "DATABASE_URL contiene un marcador de ejemplo. "
            "Configura el host real de Supabase."
        )
    return parts


def _configured_sslmode(dsn: str) -> str:
    parts = _parse_database_url(dsn)
    parameters = parse_qs(parts.query, keep_blank_values=True)
    requested = parameters.get("sslmode", [None])[-1]
    configured = str(getattr(Config, "DATABASE_SSLMODE", "require")).lower()
    sslmode = requested.lower() if requested else configured
    allowed = {"require", "verify-ca", "verify-full"}
    if sslmode not in allowed:
        raise DatabaseConfigurationError(
            "La conexión a Supabase debe utilizar sslmode=require, verify-ca o verify-full."
        )
    if requested and requested.lower() != configured:
        raise DatabaseConfigurationError(
            "El sslmode de DATABASE_URL no coincide con DATABASE_SSLMODE."
        )
    return sslmode


def _libpq_dsn(dsn: str) -> str:
    parts = _parse_database_url(dsn)
    query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key.lower() != "pgbouncer"
    ]
    return urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment)
    )


def postgres_enabled() -> bool:
    backend = str(getattr(Config, "DATA_BACKEND", "postgresql")).strip().lower()
    return backend in {"postgres", "postgresql"}


def require_postgres(*, require_enabled: bool = True) -> None:
    if require_enabled and not postgres_enabled():
        raise DatabaseConfigurationError(
            "SmartResto utiliza exclusivamente PostgreSQL. "
            "Configura DATA_BACKEND=postgresql."
        )
    if psycopg is None or dict_row is None:
        raise DatabaseConfigurationError(
            "La dependencia psycopg no está instalada. "
            "Instala psycopg[binary] desde requirements.txt."
        )
    dsn = _active_database_url()
    _parse_database_url(dsn)
    _configured_sslmode(dsn)


def isolated_query(query, conn):
    """
    Protege las consultas que se ejecutan en un esquema aislado.
    Ya no se reescribe app_records (eliminado en el modelo relacional).
    Solo se reescriben tablas heredadas para compatibilidad con tests antiguos.
    """
    schema = test_schema()
    if not schema:
        return query
    if not isinstance(query, str):
        try:
            from psycopg.sql import Composable
            if isinstance(query, Composable):
                query = query.as_string(conn)
            else:
                raise DatabaseConfigurationError(
                    "Consulta no verificable durante el aislamiento."
                )
        except ImportError:
            raise DatabaseConfigurationError(
                "No se puede verificar la consulta aislada."
            ) from None
    query = re.sub(
        r"\bpublic\.(sr_[a-z_]+|ai_decisions(?:_id_seq)?)\b",
        lambda m: schema + "." + m.group(1),
        query,
        flags=re.IGNORECASE,
    )
    if re.search(r"\bpublic\s*\.", query, flags=re.IGNORECASE):
        raise DatabaseConfigurationError(
            "Consulta bloqueada: intenta acceder al esquema public "
            "desde una prueba aislada."
        )
    if re.search(
        r"\b(DROP\s+DATABASE|ALTER\s+SYSTEM|CREATE\s+ROLE|"
        r"ALTER\s+ROLE|DROP\s+ROLE)\b",
        query,
        flags=re.IGNORECASE,
    ):
        raise DatabaseConfigurationError(
            "Operación administrativa bloqueada durante las pruebas."
        )
    return query


def transaction_limits(conn) -> None:
    statement_timeout = max(
        100,
        min(int(getattr(Config, "DATABASE_STATEMENT_TIMEOUT_MS", 8000)), 60000),
    )
    lock_timeout = max(
        100,
        min(int(getattr(Config, "DATABASE_LOCK_TIMEOUT_MS", 2000)), 10000),
    )
    conn.execute(
        """
        SELECT
            set_config('statement_timeout', %s, true),
            set_config('lock_timeout', %s, true)
        """,
        (str(statement_timeout), str(lock_timeout)),
    )


@contextmanager
def connection(*, autocommit: bool = False, require_enabled: bool = True) -> Iterator[object]:
    require_postgres(require_enabled=require_enabled)
    schema = test_schema()
    if schema and autocommit:
        raise DatabaseConfigurationError(
            "Autocommit no está permitido en pruebas aisladas."
        )
    dsn = _active_database_url()
    sslmode = _configured_sslmode(dsn)
    options = {
        "row_factory": dict_row,
        "cursor_factory": TimedCursor,
        "prepare_threshold": None,
        "connect_timeout": max(
            2, min(int(getattr(Config, "DATABASE_CONNECT_TIMEOUT", 5)), 30)
        ),
        "sslmode": sslmode,
    }
    if schema:
        options["options"] = "-c search_path=" + schema + ",pg_catalog"
    clean_dsn = _libpq_dsn(dsn)
    pool_max = max(1, min(int(getattr(Config, "DATABASE_POOL_MAX", 4)), 16))
    pool_timeout = max(0.1, min(float(getattr(Config, "DATABASE_POOL_TIMEOUT", 5)), 30.0))

    def connect():
        started = perf_counter()
        try:
            return psycopg.connect(clean_dsn, **options)
        finally:
            observe("connection_establishment", perf_counter() - started)

    pool_key = (clean_dsn, tuple(sorted(options.items())), pool_max, pool_timeout)
    pool = get_pool(pool_key, connect, maximum=pool_max, timeout=pool_timeout)
    started = perf_counter()

    try:
        conn, born = pool.acquire()
    except (PoolBusy, PoolCoolingDown):
        observe("pool_acquire", perf_counter() - started, failed=True)
        raise DatabaseConnectionError(
            "PostgreSQL está ocupado o temporalmente bloqueado. Inténtalo nuevamente."
        ) from None
    except psycopg.OperationalError as error:
        detail = str(error).lower()
        observe("pool_acquire", perf_counter() - started, failed=True)
        if any(t in detail for t in ("getaddrinfo", "11001", "11004", "name or service not known", "could not translate host")):
            message = (
                "No se pudo resolver el host PostgreSQL. Comprueba el host, "
                "el DNS y la conectividad de la conexión de Supabase."
            )
        elif any(t in detail for t in ("password authentication", "authentication failed", "tenant or user not found")):
            observe("authentication_failure", 0, failed=True)
            message = (
                "PostgreSQL rechazó la autenticación. Comprueba las credenciales "
                "y el usuario de la conexión seleccionada."
            )
        else:
            message = "No se pudo conectar a PostgreSQL. Comprueba red, puerto y TLS."
        logger.warning("Fallo de conexión PostgreSQL: %s", message)
        raise DatabaseConnectionError(message) from None
    observe("pool_acquire", perf_counter() - started)

    discard = False
    try:
        conn.autocommit = autocommit
        yield conn
        if not autocommit:
            conn.commit()
    except psycopg.OperationalError:
        discard = True
        try:
            if not autocommit:
                conn.rollback()
        except Exception:
            discard = True
        raise
    except Exception:
        if not autocommit:
            try:
                conn.rollback()
            except Exception:
                discard = True
        raise
    finally:
        pool.release(conn, born, discard=discard)


def check_connection() -> bool:
    with connection(require_enabled=False) as conn:
        transaction_limits(conn)
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 AS connected")
            row = cursor.fetchone()
            return bool(row and row["connected"] == 1)


def _required_tables() -> list[str]:
    raw = os.environ.get("SMARTRESTO_REQUIRED_TABLES", "").strip()
    if not raw:
        return []
    tables = []
    for item in raw.split(","):
        table = item.strip()
        parts = table.split(".")
        if len(parts) != 2:
            raise DatabaseConfigurationError(
                "SMARTRESTO_REQUIRED_TABLES debe utilizar el formato esquema.tabla."
            )
        schema_name, table_name = parts
        if (
            not _IDENTIFIER_PATTERN.fullmatch(schema_name)
            or not _IDENTIFIER_PATTERN.fullmatch(table_name)
        ):
            raise DatabaseConfigurationError(
                "SMARTRESTO_REQUIRED_TABLES contiene un nombre inválido."
            )
        tables.append(f"{schema_name}.{table_name}")
    return tables


def check_application_schema() -> None:
    """
    Verifica que exista el esquema y las tablas relacionales requeridas.

    IMPORTANTE: no crea tablas, no migra, no borra. Solo verifica.
    """
    schema = test_schema() or "public"
    with connection() as conn:
        transaction_limits(conn)
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s",
                (schema,),
            )
            if not cursor.fetchone():
                raise DatabaseConfigurationError(
                    f"No existe el esquema PostgreSQL '{schema}'."
                )
            for qualified_name in _required_tables():
                cursor.execute("SELECT to_regclass(%s) AS table_name", (qualified_name,))
                row = cursor.fetchone()
                if not row or not row["table_name"]:
                    raise DatabaseConfigurationError(
                        f"Falta la tabla relacional requerida: {qualified_name}."
                    )
    logger.info("PostgreSQL disponible. Esquema verificado: %s", schema)