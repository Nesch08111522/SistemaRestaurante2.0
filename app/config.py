# app/config.py
import os
from math import isfinite
from datetime import timedelta
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=False)


def _env(name: str, default: str = "") -> str:
    value = os.environ.get(name)
    return default if value is None else value.strip()


def _flag(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(f"{name} debe ser un booleano válido.")


def _bounded_int(name, default, minimum, maximum) -> int:
    try:
        value = int(_env(name, str(default)))
    except (TypeError, ValueError) as error:
        raise RuntimeError(f"{name} debe ser un entero.") from error
    if not minimum <= value <= maximum:
        raise RuntimeError(f"{name} debe estar entre {minimum} y {maximum}.")
    return value


def _bounded_float(name, default, minimum, maximum) -> float:
    try:
        value = float(_env(name, str(default)))
    except (TypeError, ValueError) as error:
        raise RuntimeError(f"{name} debe ser un decimal.") from error
    if not isfinite(value) or not minimum <= value <= maximum:
        raise RuntimeError(f"{name} debe estar entre {minimum} y {maximum}.")
    return value


def _database_url_with_sslmode(database_url: str, sslmode: str) -> str:
    allowed = {"require", "verify-ca", "verify-full"}
    if sslmode not in allowed:
        raise RuntimeError("DATABASE_SSLMODE debe ser require, verify-ca o verify-full.")
    if not database_url:
        raise RuntimeError("DATABASE_URL no está configurada.")
    try:
        parsed = urlsplit(database_url)
        if parsed.scheme.lower() not in {"postgres", "postgresql"}:
            raise RuntimeError("DATABASE_URL debe usar postgres:// o postgresql://.")
        if not parsed.hostname:
            raise RuntimeError("DATABASE_URL sin host válido.")
        if not parsed.path or parsed.path.strip("/") == "":
            raise RuntimeError("DATABASE_URL debe especificar la base de datos.")
        _ = parsed.port
    except ValueError as error:
        raise RuntimeError("DATABASE_URL tiene formato inválido.") from error

    parameters = dict(parse_qsl(parsed.query, keep_blank_values=True))
    configured = parameters.get("sslmode")
    if configured and configured.lower() != sslmode:
        raise RuntimeError("sslmode de DATABASE_URL no coincide con DATABASE_SSLMODE.")
    parameters["sslmode"] = sslmode
    return urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, urlencode(parameters), parsed.fragment)
    )


class Config:
    # Identidad
    NOMBRE_APP = "SmartResto"
    APP_NAME = "SmartResto"
    IDIOMA = "es"
    MONEDA = "S/."
    CIUDAD = "Trujillo"
    COORDENADAS_CENTRO = (-8.1118, -79.0287)
    RADIO_MAXIMO_KM = 10
    DISTRITOS = [
        "Trujillo", "Víctor Larco", "La Esperanza", "Huanchaco",
        "Moche", "El Porvenir", "Florencia de Mora",
    ]

    # Paleta
    PALETA_PRIMARIA = "#FF385C"
    PALETA_SECUNDARIA = "#008489"
    FUENTE_PRINCIPAL = "Inter"

    # Entorno
    APP_ENV = _env("APP_ENV", "development").lower()
    DEBUG = _flag("FLASK_DEBUG", False)
    TESTING = _flag("FLASK_TESTING", APP_ENV == "test")
    SECRET_KEY = _env("SECRET_KEY")

    # Local template changes must not remain cached when debug is disabled.
    TEMPLATES_AUTO_RELOAD = APP_ENV == "development"

    # Flask
    MAX_CONTENT_LENGTH = _bounded_int("MAX_CONTENT_LENGTH", 2 * 1024 * 1024, 1024, 100 * 1024 * 1024)
    JSON_AS_ASCII = False
    PREFERRED_URL_SCHEME = "https" if APP_ENV == "production" else "http"

    # Sesiones
    SESSION_COOKIE_NAME = "smartresto_session"
    SESSION_COOKIE_SECURE = _flag("SESSION_COOKIE_SECURE", APP_ENV == "production")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_PATH = "/"
    SESSION_COOKIE_SAMESITE = _env("SESSION_COOKIE_SAMESITE", "Lax").capitalize()
    PERMANENT_SESSION_LIFETIME = timedelta(
        seconds=_bounded_int("SESSION_LIFETIME_SECONDS", 3600, 60, 31 * 24 * 60 * 60)
    )
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = SESSION_COOKIE_SAMESITE

    # CSRF
    WTF_CSRF_ENABLED = _flag("WTF_CSRF_ENABLED", not TESTING)
    # OJO: itsdangerous espera SEGUNDOS (int), NO timedelta.
    WTF_CSRF_TIME_LIMIT = _bounded_int(
        "WTF_CSRF_TIME_LIMIT",
        3600,
        60,
        24 * 60 * 60,
    )

    # Proxies
    TRUSTED_PROXY_COUNT = _bounded_int("TRUSTED_PROXY_COUNT", 0, 0, 2)

    # Imágenes
    PROFILE_IMAGE_STORAGE = _env("PROFILE_IMAGE_STORAGE", "database").lower()

    # BD
    DATA_BACKEND = _env("DATA_BACKEND", "postgresql").lower()
    DATABASE_SSLMODE = _env("DATABASE_SSLMODE", "require").lower()
    _DATABASE_URL_RAW = _env("DATABASE_URL")
    DATABASE_URL = (
        _database_url_with_sslmode(_DATABASE_URL_RAW, DATABASE_SSLMODE)
        if _DATABASE_URL_RAW else None
    )
    DATABASE_POOL_MAX = _bounded_int("DATABASE_POOL_MAX", 4, 1, 30)
    DATABASE_POOL_TIMEOUT = _bounded_float("DATABASE_POOL_TIMEOUT", 5.0, 0.1, 60.0)
    DATABASE_CONNECT_TIMEOUT = _bounded_int("DATABASE_CONNECT_TIMEOUT", 5, 1, 60)
    DATABASE_STATEMENT_TIMEOUT_MS = _bounded_int("DATABASE_STATEMENT_TIMEOUT_MS", 8000, 100, 120000)
    DATABASE_LOCK_TIMEOUT_MS = _bounded_int("DATABASE_LOCK_TIMEOUT_MS", 2000, 100, 30000)

    @classmethod
    def validate(cls, config=None):
        source = config if config is not None else cls

        def get(name):
            return source.get(name) if hasattr(source, "get") else getattr(source, name, None)

        if str(get("APP_ENV") or "").strip().lower() not in {"development", "production", "test"}:
            raise RuntimeError("APP_ENV debe ser development, production o test.")
        if str(get("APP_ENV")) == "production" and bool(get("DEBUG")):
            raise RuntimeError("FLASK_DEBUG debe estar desactivado en producción.")
        if str(get("APP_ENV")) == "production" and not bool(get("SESSION_COOKIE_SECURE")):
            raise RuntimeError("SESSION_COOKIE_SECURE=1 es obligatorio en producción.")

        secret = get("SECRET_KEY")
        if not isinstance(secret, str) or not secret:
            raise RuntimeError("SECRET_KEY no está configurada.")
        if len(secret.encode("utf-8")) < 32:
            raise RuntimeError("SECRET_KEY debe tener al menos 32 bytes.")

        if str(get("SESSION_COOKIE_SAMESITE") or "").lower() not in {"lax", "strict", "none"}:
            raise RuntimeError("SESSION_COOKIE_SAMESITE debe ser Lax, Strict o None.")

        if str(get("PROFILE_IMAGE_STORAGE") or "").lower() != "database":
            raise RuntimeError("PROFILE_IMAGE_STORAGE=database es obligatorio.")

        if str(get("DATA_BACKEND") or "").lower() not in {"postgres", "postgresql"}:
            raise RuntimeError("DATA_BACKEND=postgresql es obligatorio.")

        if str(get("DATABASE_SSLMODE") or "").lower() not in {"require", "verify-ca", "verify-full"}:
            raise RuntimeError("DATABASE_SSLMODE inválido.")

        if not get("DATABASE_URL"):
            raise RuntimeError("DATABASE_URL no está configurada.")

        normalized = _database_url_with_sslmode(get("DATABASE_URL"), get("DATABASE_SSLMODE"))
        if hasattr(source, "__setitem__"):
            source["DATABASE_URL"] = normalized
        return True