# app/models/user.py
"""
UserModel relacional (Fase 1).

Reemplaza al UserModel basado en JSONB (`app_records`).
Ahora opera sobre:
  - public.usuarios
  - public.usuarios_preferencias
  - public.usuarios_restricciones
  - public.usuarios_detalles_negocio

No existe `auth_epoch` en el .sql. Se mantiene `estado_cuenta` como
`ACTIVE` / `INACTIVE`. Cuando necesites invalidar sesiones, actualiza
`actualizado_en` y añade la columna en una migración futura.
"""
from __future__ import annotations

import logging

from typing import Any

from werkzeug.security import generate_password_hash, check_password_hash

from app.repositories.usuarios import (
    UsuariosRepository,
    UsuariosPreferenciasRepository,
    UsuariosRestriccionesRepository,
    UsuariosDetallesNegocioRepository,
)
from app.db.repository import shared_transaction


logger = logging.getLogger("smartresto.auth")

from app.core.roles import canonical_role


class UserModel:
    """Fachada de usuarios sobre las 4 tablas relacionales."""

    # ---------- lectura ----------

    @staticmethod
    def is_active(user: dict | None) -> bool:
        if not user:
            return False
        if user.get("activacion_pendiente") not in (None, False):
            return False
        # Legacy rows used SQL NULL for enabled accounts. Only accept that
        # representation when activation is explicitly complete (not missing).
        key = "estado_cuenta" if "estado_cuenta" in user else "status"
        if key not in user:
            return False
        estado = user[key]
        if estado is None:
            return user.get("activacion_pendiente") is False
        return isinstance(estado, str) and estado.strip().upper() == "ACTIVE"

    @classmethod
    def get_by_id(cls, user_id: int) -> dict[str, Any] | None:
        row = UsuariosRepository.get_by_id(user_id)
        if not row:
            return None
        return cls._enrich(row)

    @classmethod
    def get_session_account(cls, user_id: int) -> dict[str, Any] | None:
        """One database read; authorization needs no preference/business queries."""
        row = UsuariosRepository.get_by_id(user_id)
        return cls._enrich(row, details=False) if row else None

    @classmethod
    def get_by_username(cls, username: str) -> dict[str, Any] | None:
        row = UsuariosRepository.get_by_username(username)
        if not row:
            return None
        return cls._enrich(row)

    @classmethod
    def _enrich(cls, row: dict[str, Any], *, details: bool = True) -> dict[str, Any]:
        """
        Convierte una fila plana de usuarios en el dict que espera la app
        (con `profile`, `preferences`, `restrictions`, `business_details`).
        """
        user_id = row["id_usuario"]
        return {
            "id": user_id,
            "username": row["nombre_usuario"],
            "password": row["hash_contrasena"],
            "role": canonical_role(row["rol"]),
            "status": row.get("estado_cuenta"),
            "activacion_pendiente": row.get("activacion_pendiente"),
            "profile": {
                "name": row.get("nombre_mostrar") or "",
                "email": row.get("correo") or "",
                "preferences": UsuariosPreferenciasRepository.list_for_user(user_id) if details else [],
                "restrictions": UsuariosRestriccionesRepository.list_for_user(user_id) if details else [],
            },
            "business_details": UsuariosDetallesNegocioRepository.get_for_user(user_id) if details else None,
            "created_at": row.get("creado_en"),
            "updated_at": row.get("actualizado_en"),
        }

    # ---------- autenticación ----------

    @classmethod
    def authenticate(cls, username: str, password: str) -> dict[str, Any] | None:
        row = UsuariosRepository.get_by_login(username)
        user = cls._enrich(row, details=False) if row else None
        if user is None:
            logger.warning("auth_rejected reason=account_not_found_or_ambiguous_email")
            return None
        if not cls.is_active(user):
            logger.warning("auth_rejected reason=account_not_active")
            return None
        password_hash = user.get("password")
        if not isinstance(password_hash, str) or not password_hash:
            logger.warning("auth_rejected reason=password_hash_missing")
            return None
        if not password_hash.startswith(("scrypt:", "pbkdf2:")):
            # Never print the hash, password or login identifier.
            family = "bcrypt" if password_hash.startswith(("$2a$", "$2b$", "$2y$")) else "argon2" if password_hash.startswith("$argon2") else "unknown"
            logger.warning("auth_rejected reason=password_format_unsupported format=%s", family)
            return None
        try:
            valid = check_password_hash(password_hash, password)
        except (ValueError, TypeError):
            logger.warning("auth_rejected reason=password_hash_invalid")
            return None
        if not valid:
            logger.warning("auth_rejected reason=password_mismatch")
        return user if valid else None

    # ---------- registro ----------

    @classmethod
    def register(
        cls,
        username: str,
        password: str,
        email: str,
        name: str,
        role: str = "user",
    ) -> dict[str, Any] | None:
        if cls.get_by_username(username):
            return None
        with shared_transaction():
            row = UsuariosRepository.insert(
                nombre_usuario=username,
                hash_contrasena=generate_password_hash(password),
                rol=role,
                nombre_mostrar=name,
                correo=email,
                estado_cuenta="ACTIVE",
                activacion_pendiente=False,
            )
        return cls._enrich(row)

    # ---------- actualizaciones ----------

    @classmethod
    def update_user(cls, user_id: int, changes: dict[str, Any]) -> dict[str, Any] | None:
        """
        Acepta un dict flexible con claves reconocidas:
          - username / nombre_usuario
          - name / nombre_mostrar
          - email / correo
          - status / estado_cuenta
          - role / rol
          - preferences (lista)  -> reemplaza usuarios_preferencias
          - restrictions (lista) -> reemplaza usuarios_restricciones
          - business_details (dict) -> upsert usuarios_detalles_negocio
        """
        if not changes:
            return cls.get_by_id(user_id)

        main_fields: dict[str, Any] = {}
        alias = {
            "username": "nombre_usuario",
            "name": "nombre_mostrar",
            "email": "correo",
            "status": "estado_cuenta",
            "role": "rol",
        }
        for src, dst in alias.items():
            if src in changes and changes[src] is not None:
                value = changes[src]
                if dst == "correo":
                    value = (value or "").lower() or None
                main_fields[dst] = value

        with shared_transaction():
            if main_fields:
                UsuariosRepository.update_fields(user_id, main_fields)

            if "preferences" in changes and isinstance(changes["preferences"], list):
                UsuariosPreferenciasRepository.replace_for_user(
                    user_id, changes["preferences"]
                )

            if "restrictions" in changes and isinstance(changes["restrictions"], list):
                UsuariosRestriccionesRepository.replace_for_user(
                    user_id, changes["restrictions"]
                )

            if "business_details" in changes and isinstance(
                changes["business_details"], dict
            ):
                bd = changes["business_details"]
                UsuariosDetallesNegocioRepository.upsert_for_user(
                    user_id,
                    nombre_negocio=bd.get("nombre_negocio"),
                    telefono=bd.get("telefono"),
                    distrito=bd.get("distrito"),
                )

        return cls.get_by_id(user_id)

    @classmethod
    def delete_user(cls, user_id: int) -> bool:
        return UsuariosRepository.delete(user_id)

    # ---------- helpers de rol ----------

    @classmethod
    def is_admin(cls, user_id: int) -> bool:
        user = UsuariosRepository.get_by_id(user_id)
        return bool(user) and canonical_role(user.get("rol")) == "admin"

    @classmethod
    def is_business_owner(cls, user_id: int) -> bool:
        user = UsuariosRepository.get_by_id(user_id)
        return bool(user) and canonical_role(user.get("rol")) == "business_owner"