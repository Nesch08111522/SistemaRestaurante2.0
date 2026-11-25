"""Password-recovery use case backed by PostgreSQL security tables.

This module deliberately stores only HMAC hashes of reset secrets.  Passwords,
one-time codes and destinations are never logged or returned to a caller.
"""
from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Literal

from flask import current_app
from werkzeug.security import generate_password_hash

from app.db.repository import shared_transaction
from app.models.user import UserModel
from app.repositories.seguridad import DesafiosContrasenaRepository
from app.repositories.usuarios import UsuariosRepository
from app.services.errors import DomainError

Channel = Literal["email", "sms"]
_CODE = re.compile(r"^[0-9]{6}$")
_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
_PHONE = re.compile(r"^\+[1-9]\d{7,14}$")
_MAX_ATTEMPTS = 5
_TTL = timedelta(minutes=10)


def password_is_valid(password: str) -> bool:
    """Return whether a password satisfies the server-side baseline policy."""
    return (
        isinstance(password, str)
        and 8 <= len(password) <= 256
        and any(char.isalpha() for char in password)
        and any(char.isdigit() for char in password)
    )


def _digest(purpose: str, value: str) -> str:
    secret = current_app.secret_key
    if not isinstance(secret, str) or not secret:
        raise RuntimeError("SECRET_KEY no está configurada.")
    return hmac.new(secret.encode("utf-8"), f"{purpose}\0{value}".encode("utf-8"), hashlib.sha256).hexdigest()


def _contact(user: dict, channel: Channel) -> str:
    profile = user.get("profile") or {}
    value = str(profile.get("email" if channel == "email" else "phone") or "").strip()
    valid = _EMAIL.fullmatch(value) if channel == "email" else _PHONE.fullmatch(value)
    return value if valid and "\r" not in value and "\n" not in value else ""


def issue(username: str, channel: Channel) -> str | None:
    """Create and deliver one challenge; returns an opaque challenge id only."""
    if channel not in {"email", "sms"}:
        raise DomainError("Selecciona correo o SMS.")
    user = UserModel.get_by_username(username)
    # Keep account enumeration impossible: callers get the same successful shape.
    if not UserModel.is_active(user):
        return None
    destination = _contact(user, channel)
    if not destination:
        return None
    from app.services.security_delivery import DeliveryUnavailable, send_code

    challenge = secrets.token_urlsafe(24)
    code = f"{secrets.randbelow(1_000_000):06d}"
    now = datetime.now(timezone.utc)
    with shared_transaction():
        latest = DesafiosContrasenaRepository.latest_for_contacto(_digest("contact", destination))
        if latest and latest.get("emitido_en") and now - latest["emitido_en"] < timedelta(minutes=1):
            raise DomainError("Espera un minuto antes de solicitar otro código.", 429)
        record = DesafiosContrasenaRepository.create(
            hash_codigo=_digest("password-code", f"{user['id']}:{challenge}:{code}"),
            codigo_desafio=challenge,
            canal=channel,
            hash_contacto=_digest("contact", destination),
            vence_en=now + _TTL,
        )
    try:
        send_code(channel, destination, code, challenge)
    except DeliveryUnavailable as exc:
        current_app.logger.warning("password_recovery_delivery_failed reason=%s", exc)
        raise DomainError("No se pudo enviar el código. Inténtalo más tarde.", 503) from None
    DesafiosContrasenaRepository.mark_delivered(record["id_desafio"])
    return challenge


def complete(username: str, challenge: str, code: str, new_password: str) -> bool:
    """Consume a valid challenge and replace the password atomically."""
    if not _CODE.fullmatch(code or "") or not isinstance(challenge, str) or len(challenge) > 128:
        return False
    if not password_is_valid(new_password):
        raise DomainError("La contraseña debe tener entre 8 y 256 caracteres, letras y números.")
    user = UserModel.get_by_username(username)
    if not UserModel.is_active(user):
        return False
    with shared_transaction():
        # The opaque challenge is the lookup key; its stored channel is then used
        # to re-check that the recovery contact has not changed.
        row = None
        for candidate_channel in ("email", "sms"):
            candidate = DesafiosContrasenaRepository.latest_for_contacto(
                _digest("contact", _contact(user, candidate_channel))
            )
            if candidate and candidate.get("codigo_desafio") == challenge:
                row = candidate
                break
        if not row or row.get("codigo_desafio") != challenge or row.get("utilizado") or not row.get("entregado"):
            return False
        if row.get("vence_en") is None or row["vence_en"] <= datetime.now(timezone.utc) or int(row.get("intentos") or 0) >= _MAX_ATTEMPTS:
            return False
        DesafiosContrasenaRepository.increment_attempts(row["id_desafio"])
        expected = _digest("password-code", f"{user['id']}:{challenge}:{code}")
        if not hmac.compare_digest(str(row.get("hash_codigo") or ""), expected):
            return False
        UsuariosRepository.set_password_hash(user["id"], generate_password_hash(new_password))
        DesafiosContrasenaRepository.mark_used(row["id_desafio"])
    return True
